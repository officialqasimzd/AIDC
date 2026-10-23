"""Tests for the Week 3 validator.

Run them from the project root:

    pytest -q

Six tests fail when you start. Each one names a check you have to write in
`src/validate_data.py`. Work through them one at a time and re-run.

These tests use tiny made-up frames rather than your data file, so a test tells
you whether your rule is correct, not whether your file happens to be clean.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import validate_data as vd  # noqa: E402


def frame(rows: list[dict]) -> pd.DataFrame:
    """Build a small frame with the contracted columns."""
    return pd.DataFrame(rows, columns=vd.REQUIRED_COLUMNS)


def row(**overrides) -> dict:
    base = {
        "timestamp": "2026-01-12T08:00",
        "line_id": "Line_A",
        "shift": "Day",
        "units_produced": 400,
        "downtime_min": 10.0,
        "energy_kwh": 160.0,
        "rejected_units": 5,
        "motor_temp_c": 75.0,
    }
    base.update(overrides)
    return base


def hours(line: str, count: int, start_hour: int = 0) -> list[dict]:
    """A run of hourly records for one line, with correct shift labels."""
    out = []
    for step in range(count):
        hour = (start_hour + step) % 24
        out.append(row(
            timestamp=f"2026-01-12T{hour:02d}:00",
            line_id=line,
            shift="Day" if 6 <= hour < 18 else "Night",
        ))
    return out


def full_day() -> list[dict]:
    return hours("Line_A", 24) + hours("Line_B", 24) + hours("Line_C", 24)


# --- worked examples: these pass from the start -----------------------------

def test_required_columns_detects_a_dropped_column():
    good = frame([row()])
    assert vd.check_required_columns(good).passed
    assert not vd.check_required_columns(good.drop(columns=["energy_kwh"])).passed


def test_required_values_complete_flags_a_blank():
    result = vd.check_required_values_complete(frame([row(), row(downtime_min=None)]))
    assert not result.passed
    assert result.affected_rows == [3]  # header is line 1, so the second record is line 3


# --- your work --------------------------------------------------------------

def test_business_key_uniqueness_flags_a_repeated_line_hour():
    clean = frame([row(), row(timestamp="2026-01-12T09:00")])
    assert vd.check_business_key_uniqueness(clean).passed

    # Same line-hour twice, disagreeing about output: both records are suspect.
    conflicted = frame([row(), row(units_produced=470)])
    result = vd.check_business_key_uniqueness(conflicted)
    assert not result.passed
    assert result.affected_rows == [2, 3]


def test_business_key_uniqueness_is_not_just_exact_duplication():
    conflicted = frame([row(), row(units_produced=470)])
    assert vd.check_exact_row_uniqueness(conflicted).passed
    assert not vd.check_business_key_uniqueness(conflicted).passed


@pytest.mark.parametrize("bad_id", ["Line_D", "line_a", "LINE_B", "Line_A "])
def test_known_line_ids_rejects_unexpected_values(bad_id):
    assert vd.check_known_line_ids(frame([row()])).passed
    assert not vd.check_known_line_ids(frame([row(line_id=bad_id)])).passed


def test_positive_energy_rejects_zero_and_negative():
    assert vd.check_positive_energy(frame([row(energy_kwh=0.1)])).passed
    assert not vd.check_positive_energy(frame([row(energy_kwh=0.0)])).passed
    result = vd.check_positive_energy(frame([row(), row(energy_kwh=-12.0)]))
    assert result.affected_rows == [3]


def test_rejects_within_output_compares_the_two_counts():
    assert vd.check_rejects_within_output(frame([row(units_produced=400, rejected_units=400)])).passed
    assert not vd.check_rejects_within_output(frame([row(units_produced=400, rejected_units=401)])).passed
    assert not vd.check_rejects_within_output(frame([row(rejected_units=-1)])).passed


def test_shift_matches_hour_uses_the_course_rule():
    assert vd.check_shift_matches_hour(frame([
        row(timestamp="2026-01-12T06:00", shift="Day"),
        row(timestamp="2026-01-12T17:00", shift="Day"),
        row(timestamp="2026-01-12T18:00", shift="Night"),
        row(timestamp="2026-01-12T05:00", shift="Night"),
    ])).passed

    wrong = frame([row(timestamp="2026-01-12T23:00", shift="Day")])
    assert not vd.check_shift_matches_hour(wrong).passed


def test_shift_matches_hour_ignores_an_unparseable_timestamp():
    # An unreadable timestamp is already reported by timestamp_parse. Reporting
    # it again here would count one fault twice.
    unreadable = frame([row(timestamp="12/01/2026 23:00", shift="Day")])
    assert vd.check_shift_matches_hour(unreadable).passed


def test_expected_line_hour_coverage_counts_distinct_hours_per_line():
    assert vd.check_expected_line_hour_coverage(frame(full_day())).passed

    short = frame(hours("Line_A", 23) + hours("Line_B", 24) + hours("Line_C", 24))
    result = vd.check_expected_line_hour_coverage(short)
    assert not result.passed
    assert result.observed["Line_A"] == 23


def test_expected_line_hour_coverage_is_not_fooled_by_a_duplicate():
    # 24 rows for Line_A, but one hour appears twice and one is missing.
    rows = hours("Line_A", 23) + [row(timestamp="2026-01-12T00:00", shift="Night")]
    disguised = frame(rows + hours("Line_B", 24) + hours("Line_C", 24))
    assert not vd.check_expected_line_hour_coverage(disguised).passed


def test_full_downtime_cannot_report_output():
    assert vd.check_full_downtime_has_no_output(
        frame([row(downtime_min=59.9, units_produced=400)])
    ).passed
    result = vd.check_full_downtime_has_no_output(
        frame([row(downtime_min=60, units_produced=400)])
    )
    assert not result.passed
    assert result.affected_rows == [2]


# --- rules that apply to every check ---------------------------------------

def run_or_skip(check, data):
    """Run a check, or skip quietly while it is still a TODO.

    These two tests apply to every check, so without this an unwritten check
    would report twice and bury the test that actually names your next task.
    """
    try:
        return check(data)
    except NotImplementedError:
        pytest.skip(f"{check.__name__} is not written yet")


@pytest.mark.parametrize("check", vd.CHECKS, ids=lambda c: c.__name__)
def test_no_check_alters_the_data(check):
    """A check produces evidence. It never repairs the frame it was given."""
    original = frame(full_day())
    copy = original.copy(deep=True)
    run_or_skip(check, original)
    pd.testing.assert_frame_equal(original, copy)


@pytest.mark.parametrize("check", vd.CHECKS, ids=lambda c: c.__name__)
def test_every_check_states_an_expectation_in_words(check):
    result = run_or_skip(check, frame(full_day()))
    assert result.expectation.strip(), f"{check.__name__} needs a readable expectation"
    assert len(result.expectation.split()) >= 5
