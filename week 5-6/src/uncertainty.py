"""How far to trust the Part C model, and how much margin to book.

Part C of the lab gave you a regression that predicts next hour's energy for
each line. This module asks the uncertainty questions of it:

- how much its misses spread (s, the residual spread);
- whether the misses run in streaks, hour after hour (lag-1 autocorrelation);
- how much its coefficients move when one training day is left out (a
  sensitivity range, which is different from a confidence interval);
- what margin to add to the prediction when booking energy, given the price
  of booking too little against booking too much.

The booking story. At the top of each hour the plant books next hour's energy
with its supplier. Energy used beyond the booking is bought at the imbalance
price; energy booked and not used is paid for anyway. For this lab a kWh short
costs three times a kWh over. The ratio is illustrative, and it is set in one
place, PRICE_SHORT and PRICE_OVER below. In the lecture's notation these are
Cu, the cost per unit of unmet demand, and Co, the cost per unit of excess.
 
Six functions are written for you as worked examples. Three are marked TODO
and are your work in this lab. Run the tests to see which are outstanding:

    pytest -q

Sign convention, as in the lecture: a residual is e = y - y_hat, what happened
minus what was predicted, so a positive residual is an hour the prediction was
short. A booking is q = y_hat + m, the prediction plus a margin.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from baselines import TARGET, fit_regression, same_hour_yesterday, next_hour_is_night

# The price of each kind of mistake, per kWh. Illustrative: change them here,
# never inside a function, so every result in the notebook moves together.
PRICE_SHORT = 3.0
PRICE_OVER = 1.0


# ------------------------------------------------------- worked examples
def add_candidate_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Worked example: add the features the notebook offers you, within each line.

    Every column added here passes the top-of-the-hour test:

    - next_hour_night: from the clock;
    - energy_last_hour: the hour before this one, already metered;
    - energy_same_hour_yesterday: next hour's value 24 hours earlier, which is
      23 rows back (Part B's alignment), NaN on the first day.
 
    The frame must already be sorted by line and time, as load_log leaves it.
    """
    out = frame.copy()
    out["next_hour_night"] = next_hour_is_night(out)
    out["energy_last_hour"] = out.groupby("line_id")["energy_kwh"].shift(1)
    out["energy_same_hour_yesterday"] = same_hour_yesterday(out)
    return out


def residuals(actual: pd.Series, predicted: pd.Series) -> pd.Series:
    """Worked example: what happened minus what was predicted, row by row.

    NaN where either value is missing, so a gap stays a gap and is never
    counted as a perfect prediction.
    """
    return (actual - predicted).rename("residual")


def share_within(resid: pd.Series, half_width: float) -> float:
    """Worked example: the fraction of residuals no further than half_width from zero.

    Use it as an empirical coverage diagnostic. y_hat +/- 1.96 s is a nominal
    range: it would hold about 95% of hours if the misses were independent,
    normal, equally spread throughout, and s were known exactly. On real data
    none of that is guaranteed, so this function counts how many held-out
    hours actually fell inside. The answer is a check on the range, and it does
    not turn the range into a calibrated 95% prediction interval. Missing
    residuals are ignored.
    """
    r = resid.dropna()
    if r.empty:
        return float("nan")
    return float((r.abs() <= half_width).mean())


def refit_leaving_out_each_day(features: pd.DataFrame, target: pd.Series,
                               timestamps: pd.Series) -> pd.DataFrame:
    """Worked example: refit once per training day, with that day left out.

    Returns one row per day left out and one column per coefficient. The lowest
    and highest value a coefficient takes across the rows is its
    leave-one-day-out sensitivity range: how much the number depends on which
    days happened to be in the training data. It is a sensitivity check, and it
    carries no 95% or other probability statement, so do not call it a
    confidence interval. Whole days are left out together so that hours which
    belong to the same day, and may share a streak of misses, stay together.
    """
    days = timestamps.dt.normalize()
    rows = {}
    for day in sorted(days.unique()):
        keep = days != day
        rows[pd.Timestamp(day).strftime("%Y-%m-%d")] = fit_regression(
            features.loc[keep], target.loc[keep])
    out = pd.DataFrame(rows).T
    out.index.name = "day_left_out"
    return out


def booking_cost(actual: pd.Series, booked: pd.Series,
                 price_short: float = PRICE_SHORT,
                 price_over: float = PRICE_OVER) -> dict:
    """Worked example: what a booking cost, hour by hour, added up.

    kWh short is energy used beyond the booking; kWh over is energy booked and
    not used. The cost is kWh over x price_over + kWh short x price_short, in
    the same units as the prices. Hours with a missing value are left out and
    the number of hours scored is reported, so two bookings can be checked for
    covering the same hours.
    """
    pair = pd.concat([actual, booked], axis=1).dropna()
    diff = pair.iloc[:, 0] - pair.iloc[:, 1]
    short = diff.clip(lower=0.0)
    over = (-diff).clip(lower=0.0)
    return {
        "kwh_over": round(float(over.sum()), 1),
        "kwh_short": round(float(short.sum()), 1),
        "hours_short": int((diff > 0).sum()),
        "cost": round(float(over.sum() * price_over + short.sum() * price_short), 1),
        "hours_scored": int(len(pair)),
    }


def booking_scorecard(actual: pd.Series, bookings: dict[str, pd.Series],
                      price_short: float = PRICE_SHORT,
                      price_over: float = PRICE_OVER) -> pd.DataFrame:
    """Worked example: one row per booking, on the same hours, at the same prices."""
    rows = [{"booking": name, **booking_cost(actual, booked, price_short, price_over)}
            for name, booked in bookings.items()]
    return pd.DataFrame(rows).set_index("booking")


# ------------------------------------------------------------- your work
def residual_spread(resid: pd.Series, n_params: int) -> float:
    """s: the typical size of a miss, allowing for the numbers that were fitted.

        s = sqrt( sum of squared residuals / (n - n_params) )

    n is the number of residuals that are not missing. n_params is how many
    numbers the model fitted from the same rows, intercept included: the
    lecture's 48 was one number fitted from six promotions, so it divided by
    6 - 1 = 5. A regression with an intercept and two features divides by
    n - 3. Missing residuals are ignored.

    Raises ValueError if n is not larger than n_params, since the spread is
    then undefined.
    """
    values = resid.dropna().to_numpy(dtype=float)
    n = len(values)
    if n <= n_params:
        raise ValueError("n must be larger than n_params")
    return float(np.sqrt(np.sum(values ** 2) / (n - n_params)))



def lag1_autocorrelation(resid: pd.Series, line_id: pd.Series) -> float:
    """Do misses run in streaks? The correlation of each residual with the one before it.

    Pairs are formed within a line only: the last hour of Line_A and the first
    hour of Line_B are not neighbours. Pairs with a missing value are dropped.
    The frame must be sorted by line and time, as load_log leaves it.

    Near 0: each hour's miss says little about the next, and the hours behave
    roughly as independent evidence. Clearly positive: misses come in runs,
    and a textbook interval computed as if every hour were independent will
    be too narrow.
    """
    previous = resid.groupby(line_id).shift(1)
    pair = pd.concat([resid, previous], axis=1).dropna()
    if len(pair) < 2:
        return float("nan")
    return float(pair.iloc[:, 0].corr(pair.iloc[:, 1]))



def margin_for_price(train_resid: pd.Series,
                     price_short: float = PRICE_SHORT,
                     price_over: float = PRICE_OVER) -> float:
    """The margin to add to a prediction, chosen from training residuals and the price.

    With Cu = price_short and Co = price_over, the cheapest booking q satisfies
    F(q) = Cu / (Cu + Co): it is short on a fraction Co / (Cu + Co) of hours.
    Since q = y_hat + m and e = y - y_hat, the margin m is the empirical quantile
    of the training residuals at Cu / (Cu + Co). At 3 to 1 that is the 75th
    percentile. Use numpy's default (linear) quantile. Missing residuals are
    ignored.

    Raises ValueError if either price is not positive.
    """
    if price_short <= 0 or price_over <= 0:
        raise ValueError("prices must be positive")
    values = train_resid.dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return float("nan")
    quantile = price_short / (price_short + price_over)
    return float(np.quantile(values, quantile))
