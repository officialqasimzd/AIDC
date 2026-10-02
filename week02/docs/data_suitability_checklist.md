# Data suitability checklist

Use **Yes**, **Partly**, **No**, or **Unknown**. Add evidence for every answer.

| Check | Rating | Evidence or unresolved question |
|---|---|---|
| Source is recorded | Yes | Applied Teaching course dataset, named Plant Shift Log. |
| Licence or permitted use is recorded | Partly | Course and educational use is permitted, but no formal licence is stated. |
| Data status is clear | Yes | The data is simulated teaching data. |
| Personal or sensitive fields are identified | Yes | No worker or customer fields are present; the fields are operational measures. |
| Unit of observation is understood | Yes | Each row is one hourly production record for one line and shift. |
| Variables match the proposed decision | Partly | Downtime, rejects, energy, and temperature support inspection prioritisation, but maintenance causes and costs are missing. |
| Time span represents the intended use | No | The log covers only 24 hourly periods from 2026-01-12 to 2026-01-13. |
| Outcome or target is available if required | No | There is no confirmed inspection, failure, or maintenance outcome. |
| Missing values and duplicates are assessed | Yes | One missing downtime value and one duplicate row are recorded. |
| Impossible or implausible values are assessed | Yes | One negative energy value and one motor temperature above 100 C are recorded. |
| Dataset size is manageable this semester | Yes | It contains 73 rows and 8 columns. |
| Stakeholder or domain evidence is available | Partly | The proposed user is an operations manager, but domain review of priorities is still needed. |
| Required permission or ethics review is known | Partly | Course use is permitted; approval for operational use and formal ethics review are unknown. |
| Client, cross-border, or confidentiality obligations are identified | Unknown | No such obligations are documented; this should be confirmed before wider use. |
| Human review and non-use conditions are defined | Yes | An operations manager or maintenance lead must review results; no automatic action is allowed. |

## Preliminary decision

Select one: **Proceed / Pilot / Change question / Stop**

**Pilot**

## Justification

The proposed user is the operations manager, who may use the Plant Shift Log to
choose which production line to inspect first. A small, transparent pilot is
appropriate because the 73-row, 8-column dataset includes useful line-level
measures: downtime, rejected units, energy use, motor temperature, output,
timestamp, line, and shift. These variables can support an initial comparison
of Line_A, Line_B, and Line_C. However, the data is simulated, covers only one
day, and has one duplicate row, one missing downtime value, one negative energy
value, and one temperature above 100 C. It has no maintenance history, failure
outcome, inspection result, product context, staffing information, or cost
data. Therefore, it cannot validate a production model or trigger automatic
maintenance. The pilot should provide exploratory summaries and a suggested
inspection priority for human review by the operations manager or maintenance
lead. The main risks are an unnecessary inspection, production delay, or a
missed equipment problem. The most important unresolved questions are whether
the sensor values are valid and whether longer logs and maintenance outcomes
are available. Use must stop if authority, data quality, or review conditions
are unclear.
