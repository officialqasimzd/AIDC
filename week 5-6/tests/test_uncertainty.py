"""Tests for the uncertainty functions, Part D.

Run them from the project root:

    pytest -q

Eight tests here fail when you start: six name a function you have to write
in `src/uncertainty.py`, and two worked examples (`add_candidate_features`,
`refit_leaving_out_each_day`) call Part B functions and turn green once those
are written. With `tests/test_baselines.py`, 14 fail at the start, 6 after
Part B, and none after Part D. Where possible the test uses the lecture's own numbers,
so a passing test also means you can check the function by hand.

Like the baseline tests, these use tiny made-up series rather than your data file.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from uncertainty import (  # noqa: E402
    PRICE_OVER,
    PRICE_SHORT,
    add_candidate_features,
    booking_cost,
    lag1_autocorrelation,
    margin_for_price,
    refit_leaving_out_each_day,
    residual_spread,
    residuals,
    share_within,
)

# The six promotions from the lecture, as distances from 48.
PROMOTION_MISSES = pd.Series([-4.0, 3.0, -2.0, 5.0, -3.0, 1.0])


# ------------------------------------------------- worked examples: green
def test_prices_are_three_to_one():
    assert PRICE_SHORT / PRICE_OVER == 3.0


def test_residual_is_actual_minus_predicted():
    r = residuals(pd.Series([10.0, 10.0, np.nan]), pd.Series([8.0, 12.0, 9.0]))
    assert r.iloc[0] == 2.0                      # prediction was short: positive
    assert r.iloc[1] == -2.0
    assert np.isnan(r.iloc[2])                   # a gap stays a gap


def test_share_within_counts_the_edge_as_inside():
    assert share_within(pd.Series([-2.0, 1.0, 3.0, np.nan]), 2.0) == pytest.approx(2 / 3)


def test_booking_cost_matches_the_bakery_week():
    # This week's bread against the prediction + 3: 19 over, 1 short, cost 22.
    sold = pd.Series([122, 121, 119, 134, 210, 185, 98], dtype=float)
    booked = pd.Series([123, 121, 128, 133, 211, 193, 98], dtype=float)
    out = booking_cost(sold, booked)
    assert (out["kwh_over"], out["kwh_short"], out["hours_short"], out["cost"]) == (19.0, 1.0, 1, 22.0)
    assert out["hours_scored"] == 7


def test_candidate_features_stay_within_each_line():
    stamps = pd.date_range("2026-01-12 06:00", periods=30, freq="h")
    rows = [{"timestamp": t, "line_id": line, "energy_kwh": float(off + i), "hour": t.hour}
            for line, off in (("Line_A", 0), ("Line_B", 100)) for i, t in enumerate(stamps)]
    out = add_candidate_features(pd.DataFrame(rows))
    b = out[out.line_id == "Line_B"]
    assert np.isnan(b["energy_last_hour"].iloc[0])           # never borrows Line_A's last hour
    assert b["energy_last_hour"].iloc[1] == 100.0
    assert b["energy_same_hour_yesterday"].iloc[23] == 100.0  # 23 rows back, as in Part B


def test_refit_leaving_out_each_day_gives_one_row_per_day():
    stamps = pd.Series(pd.date_range("2026-01-12 00:00", periods=72, freq="h"))
    x = pd.DataFrame({"x": np.arange(72, dtype=float)})
    y = 2.0 + 3.0 * x["x"]
    out = refit_leaving_out_each_day(x, y, stamps)
    assert list(out.index) == ["2026-01-12", "2026-01-13", "2026-01-14"]
    assert np.allclose(out["x"], 3.0) and np.allclose(out["intercept"], 2.0)


# ------------------------------------------------------ your work: red
def test_residual_spread_reproduces_the_lecture():
    """TODO 1. Six promotions, one fitted number: sqrt(64 / 5) = 3.58."""
    assert residual_spread(PROMOTION_MISSES, n_params=1) == pytest.approx(math.sqrt(64 / 5))


def test_residual_spread_ignores_gaps_and_refuses_too_few():
    """TODO 1. A missing residual is not a zero; and n must exceed n_params."""
    with_gap = pd.concat([PROMOTION_MISSES, pd.Series([np.nan])], ignore_index=True)
    assert residual_spread(with_gap, n_params=1) == pytest.approx(math.sqrt(64 / 5))
    with pytest.raises(ValueError):
        residual_spread(pd.Series([1.0, -1.0, np.nan]), n_params=2)


def test_lag1_autocorrelation_sees_a_seesaw():
    """TODO 2. Misses that flip sign every hour have a correlation of -1."""
    r = pd.Series([1.0, -1.0, 1.0, -1.0, 1.0, -1.0])
    line = pd.Series(["Line_A"] * 6)
    assert lag1_autocorrelation(r, line) == pytest.approx(-1.0)


def test_lag1_autocorrelation_never_pairs_across_lines():
    """TODO 2. Line_A's last hour is not Line_B's previous hour.

    Within each line the misses alternate, so the answer is exactly -1. Pairing
    Line_A's last value (-1) with Line_B's first (-1) would spoil that.
    """
    r = pd.Series([1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0])
    line = pd.Series(["Line_A"] * 4 + ["Line_B"] * 4)
    assert lag1_autocorrelation(r, line) == pytest.approx(-1.0)


def test_margin_for_price_is_the_right_quantile():
    """TODO 3. 1:1 aims at the middle; 3:1 takes the 75th percentile."""
    r = pd.Series([-2.0, -1.0, 0.0, 1.0, 2.0])
    assert margin_for_price(r, price_short=1.0, price_over=1.0) == pytest.approx(0.0)
    assert margin_for_price(r, price_short=3.0, price_over=1.0) == pytest.approx(1.0)
    assert margin_for_price(PROMOTION_MISSES) == pytest.approx(2.5)   # default 3:1


def test_margin_for_price_ignores_gaps_and_rejects_bad_prices():
    """TODO 3. Gaps are dropped; a zero or negative price makes no sense."""
    r = pd.Series([-2.0, np.nan, -1.0, 0.0, 1.0, 2.0])
    assert margin_for_price(r, 3.0, 1.0) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        margin_for_price(r, price_short=0.0, price_over=1.0)
