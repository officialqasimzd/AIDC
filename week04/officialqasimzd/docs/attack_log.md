# Week 3 Attack Log

Validation is never finished. The only way to find out what your checks miss is
to have someone try to get past them.

## The round

1. Swap validators with your partner. You now work against **their**
   `src/validate_data.py`, and they work against yours.
2. Write three rows that are **operationally nonsense** but that their checks
   **accept**. A row that fails a check is not an attack; it is a check working.
3. Append your rows to a copy of their file (`data/processed/attack_<yourname>.csv`,
   never the raw file) and run their validator to confirm it passes.
4. Hand back the rows and the log.

## My attacks on my partner's validator
 
Partner: classmate validator; name not recorded

| # | The row I wrote | Why it is nonsense in a real plant | Why their checks accepted it |
|---|---|---|---|
| 1 | `2026-01-12T08:00,Line_A,Day,400,60,160,5,75` | 60 minutes of downtime with 400 units produced is impossible | The original checks only bounded downtime and did not compare it with output |
| 2 | `2026-01-12T09:00,Line_B,Day,0,0,0.1,0,75` | A production log with zero output needs a reason, but the basic rules do not require one | It has valid types, ranges, and a unique business key |
| 3 | `2026-01-12T10:00,Line_C,Day,500,1,170,2,75` | 500 units in one hour is outside the normal line profile and needs review | No check defines an expected production range |

## Attacks that got past my validator

| # | Their row | Why my checks accepted it | The check I would add |
|---|---|---|---|
| 1 | `2026-01-12T08:00,Line_A,Day,400,60,160,5,75` | The twelve baseline checks accepted the boundary value of 60 minutes while ignoring the positive output | `full_downtime_has_no_output` |
| 2 | `2026-01-12T09:00,Line_B,Day,0,0,0.1,0,75` | The file has no rule requiring an explanation for zero production | Add a documented production-state or operating-status field |
| 3 | `2026-01-12T10:00,Line_C,Day,500,1,170,2,75` | The validator checks validity, not whether output is unusual for a line | Add an approved line-specific output review threshold |

## The check I actually added

Name it, paste the code, and say which attack it stops. Add a test for it in
`tests/test_validate_data.py` and confirm `pytest -q` is green.

```python
def check_full_downtime_has_no_output(frame):
    impossible = (
        frame["downtime_min"].notna()
        & frame["units_produced"].notna()
        & (frame["downtime_min"] == 60)
        & (frame["units_produced"] > 0)
    )
    return result(
        "full_downtime_has_no_output",
        impossible,
        "an hour with 60 minutes of downtime reports no units produced",
    )
```

## What this round changed about your approval decision

The added check makes the descriptive approval more cautious: downtime and output must be reviewed together. I still do not use the file for prediction or automatic action because the attack round showed that many plausible-looking rows need context.
