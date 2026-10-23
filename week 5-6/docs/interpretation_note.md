# Interpretation note

Student file: `data/raw/shift_week_officialqasimzd.csv`

SHA 256: `259f5b2e6d612b81a2989ce06a50c926773ec803a07131ab78ccfed4b60e2ab4`

## 1. What does it predict?

The model predicts `energy_next`, the energy in kWh that each production line will use during the next hour, for the plant operator at the top of the current hour, as shown by `TARGET` and the next hour shift in `src/baselines.py`.

## 2. What does it beat, and by how much?

The scorecard in `artifacts/scorecard.csv` reports the following results on the same 87 test hours.

Model: naive last hour, average miss 5.29 kWh, hours short 42, hours scored 87.

Model: line mean, average miss 6.52 kWh, hours short 48, hours scored 87.

Model: same hour yesterday, average miss 6.73 kWh, hours short 48, hours scored 87.

Model: regression, average miss 5.28 kWh, hours short 45, hours scored 87.

The regression beats the incumbent rule by 0.01 kWh an hour by mean absolute error on the last two test days, from the scorecard.

## 3. On which metric, and on which does it lose?

The regression wins on average miss at 5.28 kWh versus 5.29 kWh, but loses on short hours because it is short 45 times versus 42 for the rule.

## 4. What did it miss?

Every baseline misses the Line C hour beginning at 18:00 on 18 January 2026, where the rule residual is minus 42.4 kWh and the regression residual is minus 31.7 kWh, because the generated record contains a motor temperature of 112.0 degrees Celsius and an associated energy spike, which the maintenance or operations owner could explain.

## 5. What must be known at the top of the hour?

The regression uses `energy_kwh`, which is already metered in the current hour, and `next_hour_night`, which is determined from the clock and shift schedule before the next hour begins.

The column that fails the test is `energy_kwh_smoothed`, because `src/make_week.py` calculates it from the current energy and the next hour energy, so it contains future information.

## 6. Should it replace the rule?

The regression should not replace the rule solely for a 0.01 kWh hourly improvement because changing plant planning would add operational review and supplier booking risk while increasing short hours from 42 to 45.

## The sentence

The regression beats the rule by 0.01 kWh an hour on mean absolute error over the last two test days, scoring 5.28 kWh against 5.29 kWh on 87 hours.
