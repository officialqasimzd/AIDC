# Week 3 Data Quality Report

Keep this to one page. A supervisor should be able to read it in two minutes
and know what they may do with the file.

## 1. What I examined

- File name: `shift_log_officialqasimzd.csv`
- SHA-256 fingerprint: `9fd52cb5dad2e8f74ec2fd6827f93a819b43b6ceb4c36cc53cdc4709c190235d`
- Rows / columns: 73 rows / 8 columns
- One row represents: one production line during one hourly period
- The business key is: `timestamp` + `line_id`
- Reviewed by / date: Syed Muhammad Qasim Zaidi / 2026-10-07

## 2. What I found before running the validator
 
Fill this in **during Step 3 of the notebook**, before you compare against the
checks. Do not go back and improve it afterwards; the gap is the point.

| # | Record (line and hour) | What I noticed |
|---|---|---|
| 1 | Line_B at 07:00, CSV line 6 | `motor_temp_c` is 112.3 |
| 2 | Line_A at 21:00, CSV line 47 | `downtime_min` is 124.7 minutes |
| 3 | Line_B at 02:00, CSV line 63 | The timestamp is not in the stated ISO format |

## 3. What the checks found

One row per distinct problem. If one fault trips two checks, say so rather than
counting it twice.

| Check | CSV line(s) | Observation (no speculation) | Impossible or surprising? | What should happen next | Who owns it |
|---|---|---|---|---|---|
| timestamp_parse | 63 | Timestamp is `13/01/2026 02:00` rather than ISO format | Impossible under the contract | Confirm the source timestamp and record any approved correction | Data owner |
| required_values_complete | 19 | `energy_kwh` is blank | Impossible for a required field | Obtain the source meter value before use | Operations data owner |
| business_key_uniqueness | 54, 74 | The Line_B 23:00 line-hour appears twice with different values | Impossible as a unique hourly log | Reconcile the two source records | Shift supervisor |
| downtime_range | 47 | `downtime_min` is 124.7 minutes in a one-hour period | Impossible | Check the source downtime record | Shift supervisor |
| motor_temperature_review_range | 6 | `motor_temp_c` is 112.3 | Surprising, not settled from this file | Review the sensor and maintenance record | Controls team |
| shift_matches_hour | 60 | The 01:00 timestamp is labelled `Day` | Impossible under the course shift rule | Confirm the source shift label | Shift supervisor |

## 4. The gap

- Found by the checks, missed by me: the blank energy value at line 19, the repeated key at lines 54 and 74, and the shift mismatch at line 60.
- Found by me, covered by no check: none.
- The check I added or would add as a result: `full_downtime_has_no_output`, which catches positive production reported with a complete 60-minute stop.

## 5. The judgement call

The high motor temperature reading is unusual, not impossible.

- Three explanations, one of which is not a fault: a sensor fault, genuine overheating, or an unusual but valid operating load.
- The single piece of evidence that would separate them: the calibrated sensor or maintenance record for that hour.
- Who holds it: the controls or maintenance team.

## 6. What this file can and cannot support

This file can support a descriptive comparison of recorded output and downtime at the next handover, with the listed warnings shown to the supervisor. It cannot support a machine-failure prediction or an automatic intervention. A simple count of records by line is safe as a descriptive check, but a downtime or temperature trend should not be acted on until the flagged records are reviewed.
