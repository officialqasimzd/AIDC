"""Baselines for next hour's energy, per production line.

The target is energy_next: the energy a line will use in the hour after this
one. The incumbent rule, the plant's version of the manager's, is to assume
next hour looks like this one. Every model here is scored against that rule,
on the same hours, with the same metric.

Three functions are written for you as worked examples. Three are marked TODO
and are your work in this lab. Run the tests to see which ones are outstanding:

    pytest -q

A model never edits the data. It reads a frame and hands back predictions, and
the scoring functions turn predictions and actuals into one number a person can
compare.
"""

from __future__ import annotations
import numpy as np
import pandas as pd

TARGET = "energy_next"

# Columns known at the top of the hour, when the prediction has to be made.
# Anything not in this list has to be argued for in the interpretation note.
KNOWN_AT_TOP_OF_HOUR = {
    "line_id", "shift", "hour", "units_produced", "downtime_min",
    "energy_kwh", "rejected_units", "motor_temp_c",
    "energy_last_hour", "energy_same_hour_yesterday", "next_hour_night",
}


# --------------------------------------------------------------- loading
def load_log(path) -> pd.DataFrame:
    """Read a shift log and sort it so that shifting within a line is safe."""
    frame = pd.read_csv(path)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame = frame.sort_values(["line_id", "timestamp"]).reset_index(drop=True)
    frame["hour"] = frame["timestamp"].dt.hour
    return frame


def add_target(frame: pd.DataFrame) -> pd.DataFrame:
    """Worked example: attach next hour's energy to each row, within its line.

    The last hour of each line has no next hour, so those rows are dropped.
    Getting this alignment right is most of the difficulty of forecasting: a
    model that predicts this hour's energy from this hour's energy scores
    perfectly and is useless.
    """
    out = frame.copy()
    out[TARGET] = out.groupby("line_id")["energy_kwh"].shift(-1)
    return out.dropna(subset=[TARGET]).reset_index(drop=True)


def split_by_day(frame: pd.DataFrame, test_days: int = 2):
    """Worked example: the last `test_days` days are the test set.

    Time goes forward. A model is fitted on the past and scored on hours it
    never saw, in order. Shuffling rows would let it peek at the future.
    """
    days = sorted(frame["timestamp"].dt.normalize().unique())
    cutoff = days[-test_days]
    # Indices are kept, not reset, so a Series computed on the whole frame
    # can be lined up with the test rows by .loc[test.index].
    train = frame[frame["timestamp"] < cutoff]
    test = frame[frame["timestamp"] >= cutoff]
    return train, test


# ------------------------------------------------------- worked baselines
def naive_last_hour(frame: pd.DataFrame) -> pd.Series:
    """Worked example: next hour looks like this one. The incumbent rule."""
    return frame["energy_kwh"].rename("naive_last_hour")


def line_mean(train: pd.DataFrame, frame: pd.DataFrame) -> pd.Series:
    """Worked example: each line's average next-hour energy over the training days."""
    means = train.groupby("line_id")[TARGET].mean()
    return frame["line_id"].map(means).rename("line_mean")


def next_hour_is_night(frame: pd.DataFrame) -> pd.Series:
    """Worked example of a feature that passes the top-of-the-hour test.

    Whether the coming hour falls in the Night shift is known from the clock,
    so it is legitimately available when the prediction is made. It is also
    the one thing "next hour looks like this one" cannot know: the rule is
    always wrong at the two shift changes.
    """
    nxt = (frame["hour"] + 1) % 24
    return ((nxt >= 18) | (nxt < 6)).astype(int).rename("next_hour_night")


def hours_short(actual: pd.Series, predicted: pd.Series) -> int:
    """Worked example: how often the prediction was below what happened.

    The plant's version of "days the shop ran short". A model that is usually
    a little low is a different risk from one that is usually a little high,
    and the average miss cannot tell them apart.
    """
    pair = pd.concat([actual, predicted], axis=1).dropna()
    return int((pair.iloc[:, 1] < pair.iloc[:, 0]).sum())


def passes_top_of_hour_test(column: str) -> bool:
    """Worked example: is this column known when the prediction is made?"""
    return column in KNOWN_AT_TOP_OF_HOUR


def predict(features: pd.DataFrame, coefficients: pd.Series) -> pd.Series:
    """Worked example: apply fitted coefficients to a feature frame."""
    pred = pd.Series(coefficients["intercept"], index=features.index, dtype=float)
    for column in features.columns:
        pred = pred + coefficients[column] * features[column].astype(float)
    return pred.rename("regression")


# ------------------------------------------------------------- your work
def same_hour_yesterday(frame: pd.DataFrame) -> pd.Series:
    """TODO 1.

    Predict next hour's energy with the energy the same line used at that hour
    yesterday. Think carefully about the alignment: the target is the hour
    after this row, so the value you want is the energy 24 hours before *that*
    hour, which is 23 rows back within the line, not 24. Rows in the first day
    have nothing to copy and should be NaN, not zero.

    Return a Series aligned with `frame`, named "same_hour_yesterday".
    """
    return (frame.groupby("line_id")["energy_kwh"]
            .shift(23)
            .rename("same_hour_yesterday"))


def mean_absolute_error(actual: pd.Series, predicted: pd.Series) -> float:
    """TODO 2.

    The average size of the miss, ignoring direction. Pairs where either value
    is missing are left out rather than counted as zero; a baseline that has
    nothing to say for the first day should not be rewarded for it.
    """
    pair = pd.concat([actual, predicted], axis=1).dropna()
    if pair.empty:
        return float("nan")
    return float((pair.iloc[:, 0] - pair.iloc[:, 1]).abs().mean())


def fit_regression(features: pd.DataFrame, target: pd.Series) -> pd.Series:
    """TODO 3.

    Fit an ordinary least-squares line: find the intercept and one coefficient
    per feature column that make the features add up to the target as closely
    as possible. numpy.linalg.lstsq does the arithmetic; your job is to build
    the design matrix with a column of ones for the intercept and to hand back
    a Series indexed "intercept" followed by the feature names, so that
    `predict` can use it.

    Rows where any feature or the target is missing must be dropped first.
    """
    pair = pd.concat([features, target.rename(TARGET)], axis=1).dropna()
    design = np.column_stack([
        np.ones(len(pair)),
        pair[features.columns].to_numpy(dtype=float),
    ])
    coefficients, *_ = np.linalg.lstsq(
        design, pair[TARGET].to_numpy(dtype=float), rcond=None
    )
    return pd.Series(coefficients, index=["intercept", *features.columns])


# ------------------------------------------------------------- reporting
def scorecard(test: pd.DataFrame, predictions: dict[str, pd.Series]) -> pd.DataFrame:
    """One row per model: average miss and hours short, on the same test hours."""
    rows = []
    for name, pred in predictions.items():
        rows.append({"model": name,
                     "mean_absolute_error": round(mean_absolute_error(test[TARGET], pred), 2),
                     "hours_short": hours_short(test[TARGET], pred),
                     "hours_scored": int(pd.concat([test[TARGET], pred], axis=1).dropna().shape[0])})
    return pd.DataFrame(rows).set_index("model")
