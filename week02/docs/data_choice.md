# Preliminary dataset choice

- **Dataset name:** Plant Shift Log
- **Source:** Applied Teaching course dataset.
- **Licence or permitted use:** No formal licence is stated; use is permitted for this course and its educational exercises.
- **Data status:** Simulated teaching data.
- **Unit of observation:** One hourly production record for one production line and shift.
- **Time span:** 2026-01-12 06:00 to 2026-01-13 05:00, covering 24 hourly periods.
- **Number of rows and columns:** 73 rows and 8 columns.
- **Variables relevant to the decision:** Timestamp, line ID, shift, units produced, downtime minutes, energy use, rejected units, and motor temperature can help prioritise a line for inspection.
- **Important missing variables:** Maintenance history, failure causes, product type, staffing, operating conditions, maintenance cost, and confirmed inspection or failure outcomes are not recorded.
- **Known quality issues:** There is 1 duplicate row, 1 missing downtime value, 1 negative energy value, and 1 motor-temperature value above 100 C. The dataset also covers only one day.
- **Why the data may fit the question:** It contains line-level operational and quality measures that can support an initial comparison of Line_A, Line_B, and Line_C for a human-reviewed inspection priority.
- **Why the data may not fit the question:** The short observation window, small sample, missing value, duplicate, implausible values, and absent maintenance outcomes make it unsuitable for a validated production model or unattended decision.
- **Additional data or stakeholder evidence needed:** Obtain longer historical logs, maintenance and failure records, product and staffing context, sensor validation notes, cost or downtime consequences, and an operations manager's review of proposed inspection priorities.

## Intended role

**Decision-support pilot.** Use the log for exploratory summaries and a transparent,
human-reviewed prioritisation of which line to inspect first. Do not use it for
autonomous maintenance scheduling or model development until the quality issues,
short time span, and missing maintenance outcomes are addressed.
