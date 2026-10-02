# Week 2 industrial problem brief

Keep this brief to approximately one page. Use short, concrete statements.

## Decision statement

For the **operations manager**, use **hourly production and equipment measures**
to support **which production line should be inspected first** before the next
maintenance review.

## Problem frame

- **User:** Operations manager.
- **Decision owner:** Operations manager, with maintenance lead review.
- **Affected people:** Maintenance staff and production teams.
- **Data owner:** Applied Teaching course team.
- **Decision to support:** Which of Line_A, Line_B, or Line_C should be inspected first.
- **Action that may follow:** A human-approved inspection of the selected line.
- **Available evidence:** 73 hourly records with output, downtime, energy use, rejects, temperature, line, shift, and timestamp.
- **Desired value:** Prioritise inspections using clear operational evidence.
- **Technical success measure:** Produce a transparent line comparison and identify unusual values.
- **Operational success measure:** The manager can review and act on the priority before maintenance planning.
- **Guardrail:** No automatic maintenance or production decision; human review is required.
- **Baseline comparison:** Compare the transparent priority with the Week 1 rule, which selected Line_B.
- **Main constraint:** One day of simulated data with known quality issues and no maintenance outcomes.
- **Condition for non-use:** Do not use the output if data quality, sensor validity, authority, or review conditions are unclear.

## Assumptions and open questions

1. Are the negative energy value and temperature above 100 C sensor errors?
2. Can longer logs and confirmed maintenance or failure outcomes be obtained?
3. What inspection costs and approval process apply in real operations?
