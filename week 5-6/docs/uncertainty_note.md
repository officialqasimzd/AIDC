# Uncertainty and limitations note

One page. Six questions, each answered in one sentence, each sentence backed by
a number a reader can find in this repository: `artifacts/spread.csv`,
`artifacts/booking_scorecard.csv`, or a table the notebook prints. This is the
second of the lab's two deliverables. It sits beside the interpretation note
and does not replace it.

Your file: `data/raw/shift_week_<username>.csv`
SHA-256: 

The improved model: the Part C regression's features plus

## 1. What does the coefficient mean?

Take the coefficient on the feature you added, or on `next_hour_night`, and say
what it measured, in kWh, as a measurement first: *hours before a night hour
used X kWh less, other features held fixed*. Then say whether you would read it
as a cause, and why or why not.

Did the added feature improve the test score? Give both averages.

## 2. How sure is it?

Give the coefficient's leave-one-day-out sensitivity range, lowest to highest
across the refits, and how many training days it rests on (six, 12 to 17
January). Call it a sensitivity range: it shows how much the number depends on
which days were used, and it is not a 95% confidence interval.

| Coefficient | All training days | Lowest | Highest |
|---|---:|---:|---:|
|  |  |  |  |
|  |  |  |  |

## 3. How far can one hour be?

Give $s$ for the improved model, the nominal range $\hat y \pm 1.96\,s$, and its
empirical coverage: the share of test hours that actually landed inside. Say
whether the coverage is close to 95% and, if not, which of independence,
normality, a constant spread or the estimate of $s$ you suspect. Then name the
largest test miss, how far outside the range it was, and who could tell you
why.

## 4. Which assumptions did you check?

Two checks, each with its number and what it found. Say "no evidence against"
when that is what you found; passing a check means only that the data did not contradict the assumption.

| Assumption | Check | Result |
|---|---|---|
| Misses are close to independent from hour to hour | Lag-1 autocorrelation $\rho_1$ |  |
| The spread is the same before day and night hours | $s$ for each |  |

Which model's misses did run in streaks, and what does that do to any interval
computed as if its hours were independent?

## 5. Which cannot be tested yet?

Name one assumption this week of data cannot test, and what data would test it.
State it precisely: the condition, and what goes wrong under it.

## 6. Is it adequate for the booking?

Give the margin your model books at 3 to 1, its cost on the test hours, and the
rule's cost with its own margin, on the same hours at the same prices. Give the
share of test hours short against the one in four it aimed for. Say whether
the improved model with its margin is adequate for booking energy, and the
limitation you would state next to that answer.

## The sentence

One line, with a range and the count behind it. It should sound like: *booked
with a margin of X kWh, the improved model cost Y against the rule's Z on 87
test hours, and it was short on N of them.*
