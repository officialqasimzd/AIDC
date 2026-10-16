"""Tests for the baselines, Part B.

Run them from the project root:

    pytest -q

Six tests here fail when you start. Each names a function you have to write
in `src/baselines.py`; work through them one at a time and re-run. Two worked
examples in `tests/test_uncertainty.py` depend on these functions too, so 14
tests fail at the very start, 6 after Part B, and none after Part D.

These tests use tiny made-up frames rather than your data file, so a test tells
you whether your function is correct, not whether your file happens to be kind
to it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from baselines import (  # noqa: E402
    TARGET,
    add_target,
    fit_regression,
    hours_short,
    line_mean,
    mean_absolute_error,
    naive_last_hour,
    next_hour_is_night,
    passes_top_of_hour_test,
    predict,
    same_hour_yesterday,
    split_by_day,
)


def frame(hours: int, lines=("Line_A", "Line_B"), start="2026-01-12 06:00") -> pd.DataFrame:
    """A small log: energy climbs by one each hour, offset by 100 for Line_B."""
    stamps = pd.date_range(start, periods=hours, freq="h")
    rows = []
    for line in lines:
        offset = 100 if line == "Line_B" else 0
        for i, ts in enumerate(stamps):
            rows.append({"timestamp": ts, "line_id": line, "energy_kwh": float(offset + i),
                         "units_produced": 400 + i, "hour": ts.hour})
    return pd.DataFrame(rows).sort_values(["line_id", "timestamp"]).reset_index(drop=True)


# ------------------------------------------------- worked examples: green
def test_add_target_is_next_hour_within_the_line():
    out = add_target(frame(4))
    a = out[out.line_id == "Line_A"]
    assert list(a["energy_kwh"]) == [0.0, 1.0, 2.0]          # last hour dropped
    assert list(a[TARGET]) == [1.0, 2.0, 3.0]
    b = out[out.line_id == "Line_B"]
    assert list(b[TARGET]) == [101.0, 102.0, 103.0]          # never crosses lines


def test_naive_last_hour_copies_this_hour():
    out = add_target(frame(3))
    assert naive_last_hour(out).tolist() == out["energy_kwh"].tolist()


def test_line_mean_is_per_line_over_training_rows():
    out = add_target(frame(4))
    pred = line_mean(out, out)
    assert pred[out.line_id == "Line_A"].unique().tolist() == [2.0]
    assert pred[out.line_id == "Line_B"].unique().tolist() == [102.0]


def test_hours_short_counts_under_predictions_only():
    actual = pd.Series([10.0, 10.0, 10.0, np.nan])
    predicted = pd.Series([9.0, 10.0, 12.0, 5.0])
    assert hours_short(actual, predicted) == 1


def test_top_of_hour_test_rejects_the_smoothed_column():
    assert passes_top_of_hour_test("energy_kwh")
    assert passes_top_of_hour_test("energy_same_hour_yesterday")
    assert not passes_top_of_hour_test("energy_kwh_smoothed")
    assert not passes_top_of_hour_test(TARGET)


def test_predict_applies_intercept_and_coefficients():
    X = pd.DataFrame({"a": [1.0, 2.0], "b": [10.0, 20.0]})
    coef = pd.Series({"intercept": 1.0, "a": 2.0, "b": 0.5})
    assert predict(X, coef).tolist() == [8.0, 15.0]


def test_split_by_day_keeps_time_order():
    f = add_target(frame(24 * 3))
    train, test = split_by_day(f, test_days=1)
    assert train["timestamp"].max() < test["timestamp"].min()
    assert test["timestamp"].dt.normalize().nunique() == 1


def test_next_hour_is_night_flags_the_hour_before_each_shift_change():
    f = frame(24, lines=("Line_A",))                      # 06:00 .. 05:00
    flag = next_hour_is_night(f)
    assert flag.iloc[11] == 1                             # 17:00 -> 18:00 is Night
    assert flag.iloc[12] == 1
    assert flag.iloc[23] == 0                             # 05:00 -> 06:00 is Day
    assert flag.iloc[0] == 0


# ------------------------------------------------------ your work: red
def test_same_hour_yesterday_is_23_rows_back_within_the_line():
    """TODO 1. Target is the next hour, so yesterday's value for it sits 23 rows back."""
    out = add_target(frame(30, lines=("Line_A",)))
    pred = same_hour_yesterday(out)
    # row 23 has target energy at hour 24 (value 24); yesterday's same hour is value 0
    assert pred.iloc[23] == 0.0
    assert pred.iloc[28] == 5.0
    assert pred.name == "same_hour_yesterday"


def test_same_hour_yesterday_is_missing_for_the_first_day():
    """TODO 1. Nothing to copy on day one: NaN, never zero."""
    out = add_target(frame(30, lines=("Line_A", "Line_B")))
    pred = same_hour_yesterday(out)
    first_day = out.groupby("line_id").head(23).index
    assert pred.loc[first_day].isna().all()
    assert pred.notna().sum() == 2 * (29 - 23)


def test_mean_absolute_error_is_the_average_size_of_the_miss():
    """TODO 2."""
    actual = pd.Series([10.0, 20.0, 30.0])
    predicted = pd.Series([12.0, 17.0, 30.0])
    assert mean_absolute_error(actual, predicted) == pytest.approx(5.0 / 3.0)


def test_mean_absolute_error_ignores_missing_pairs():
    """TODO 2. A baseline with nothing to say for day one is not rewarded for it."""
    actual = pd.Series([10.0, 20.0, 30.0, 40.0])
    predicted = pd.Series([np.nan, 22.0, 27.0, np.nan])
    assert mean_absolute_error(actual, predicted) == pytest.approx(2.5)


def test_fit_regression_recovers_an_exact_line():
    """TODO 3. y = 2 + 3x, so the fit should find those numbers."""
    X = pd.DataFrame({"x": [0.0, 1.0, 2.0, 3.0]})
    y = pd.Series([2.0, 5.0, 8.0, 11.0])
    coef = fit_regression(X, y)
    assert list(coef.index) == ["intercept", "x"]
    assert coef["intercept"] == pytest.approx(2.0)
    assert coef["x"] == pytest.approx(3.0)


def test_fit_regression_drops_rows_with_missing_values():
    """TODO 3. A NaN in one feature removes that row, not the whole fit."""
    X = pd.DataFrame({"x": [0.0, 1.0, np.nan, 3.0], "z": [1.0, 1.0, 1.0, 1.0]})
    y = pd.Series([2.0, 5.0, 8.0, 11.0])
    coef = fit_regression(X, y)
    assert coef["x"] == pytest.approx(3.0)
    assert predict(X.iloc[[3]], coef).iloc[0] == pytest.approx(11.0)
