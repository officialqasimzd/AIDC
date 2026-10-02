# Initial ethical and operational risk note

## People and authority

- **Who may benefit:**
- Operations managers may receive a clearer first comparison of production lines. Maintenance staff and production teams may benefit from earlier, better-targeted inspections.
- **Who may be harmed, delayed, or unfairly burdened:**
- Maintenance staff may be sent to inspect a line unnecessarily, and a production line may be delayed. A missed warning could leave equipment problems unresolved. No worker-level data is available to assess individual impact.
- **Who may act on the output:**
- An operations manager may use the output to choose which line to inspect first. Maintenance staff may carry out the inspection.
- **Who can review, challenge, or stop its use:**
- The operations manager or a designated maintenance lead should review and stop use. The exact authority is not yet confirmed.

## Error consequences

- **Event being flagged:**
- A production line that may need inspection based on downtime, rejected units, energy use, and motor temperature.
- **False alarm:**
- A line is prioritised even though it does not need inspection.
- **Likely cost of a false alarm:**
- Unnecessary inspection time, maintenance cost, and possible production delay. The actual cost is unknown.
- **Missed warning:**
- A line with a developing equipment problem is not prioritised.
- **Likely cost of a missed warning:**
- Further downtime, rejected production, repair cost, or a safety concern. The actual cost is unknown.
- **Evidence needed to compare these costs:**
- Longer production logs, maintenance and failure records, inspection outcomes, downtime costs, repair costs, and an operations manager's review.

## Data rights and safeguards

- **Personal or sensitive fields present:**
- None identified. The dataset contains operational plant measures and no worker or customer information.
- **Permission or approval required:**
- Course use is permitted. Approval for operational use and any formal ethics review requirement are unknown.
- **Minimum data needed:**
- Timestamp, line ID, shift, units produced, downtime, energy use, rejected units, and motor temperature. Longer records and maintenance outcomes are needed before operational use.
- **Human oversight:**
- An operations manager or maintenance lead must review the data and priority before any inspection. The output must remain a transparent decision aid.
- **Condition for non-use:**
- Do not use the output if the data quality issues are unresolved, if sensor values are not validated, if authority is unclear, or if it would trigger automatic maintenance or production decisions.

## Initial risk judgement

The main risk is that a short and imperfect dataset could give one production
line an unjustified inspection priority. The log covers only one day and has a
duplicate row, a missing downtime value, a negative energy value, and a motor
temperature above 100 C. It also has no maintenance history or confirmed
failure outcome. A false alarm could waste maintenance time and delay
production, while a missed warning could allow equipment damage, downtime, or
a safety concern. The costs of these outcomes are not yet known. The practical
safeguard is mandatory human review: an operations manager or maintenance lead
must check the raw records, question unusual values, and approve any
inspection decision. Use the output only for a transparent pilot priority,
never for automatic scheduling. Stop use until longer logs, validated sensor
data, maintenance outcomes, and operational approval are available.
