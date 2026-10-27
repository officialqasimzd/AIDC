# Uncertainty and limitations note

Student file: `data/raw/shift_week_officialqasimzd.csv`

SHA 256: `259f5b2e6d612b81a2989ce06a50c926773ec803a07131ab78ccfed4b60e2ab4`

The improved model adds `energy_last_hour` to the Part C features `energy_kwh` and `next_hour_night`.

## 1. What does the coefficient mean?

The `energy_last_hour` coefficient is 0.243, meaning that one additional kWh in the previous hour is associated with 0.243 additional kWh in the next hour while the other features are held fixed, and this is a measurement rather than a causal claim because operating conditions can affect both hours. 
 
The added feature improves the test average miss from 5.28 kWh to 5.20 kWh, as shown by the improved model scorecard table printed by the notebook.
 
## 2. How sure is it?

The leave one day out sensitivity range rests on six training days from 12 to 17 January and is not a 95 percent confidence interval.

Coefficient `energy_last_hour`: all training days 0.243, lowest 0.218, highest 0.273.

Coefficient `next_hour_night`: all training days minus 3.658, lowest minus 3.847, highest minus 3.306.

## 3. How far can one hour be?

For the improved model, the training residual spread is 5.87 kWh, giving the nominal range prediction plus or minus 11.51 kWh, and 95 percent of the 87 test hours were inside it, which is close to the nominal 95 percent while still being only an empirical coverage check.

The largest improved model test residual is 36.4 kWh at the hour beginning 17:00 on 18 January for Line C, placing the actual value 24.9 kWh beyond the upper nominal range, and the operations or maintenance owner could explain that unusual transition.

## 4. Which assumptions did you check?

The improved residual lag one autocorrelation is 0.02, so there is no evidence against approximate independence from hour to hour in this check.

The improved residual spread is 5.89 kWh for day hours and 5.79 kWh for night hours, so there is no evidence against a similar spread between day and night hours.

The line mean model has misses that run in streaks with lag one autocorrelation 0.63, which makes an interval computed as if its hours were independent too narrow, while the improved model has autocorrelation 0.02 because it uses the current hour energy.

## 5. Which cannot be tested yet?

Seven days cannot test whether the residual distribution remains stable across seasons, products, maintenance states and unusual production loads, so several months covering those conditions would be needed before treating the spread and coverage as reliable for future periods.

## 6. Is it adequate for the booking?

At the three to one price ratio the improved model books a margin of 3.5 kWh, costs 740.3 on 87 test hours, and the rule with its 4.1 kWh margin costs 777.7, but the improved booking is short on 28 hours or 32 percent rather than the one in four target.

The improved model with its margin is not yet adequate as an automatic booking policy because its short share misses the stated target and the evidence covers only six training days and two test days.

## The sentence

Booked with a margin of 3.5 kWh, the improved model cost 740.3 against the rule cost of 777.7 on 87 test hours and was short on 28 of them, while its leave one day out coefficient range for `energy_last_hour` was 0.218 to 0.273.
