# Week 3 Dataset Approval

## The decision, in one sentence

Complete this sentence exactly. It is the sentence you would defend in a
handover meeting, and it is what you will read aloud if asked.

> This file **may** be used to support descriptive review at the next shift handover,
> but **may not** be used to predict machine failure or trigger automatic intervention,
> on condition that the malformed timestamp, blank energy value, duplicate line-hour, excessive downtime, shift mismatch, and high-temperature reading are reconciled or clearly excluded,
> and the decision is revisited when the source records and the temperature reading have been checked.

Decision: **Approve with conditions**
 
## Why this decision and not the one next to it

The file fails several quality checks, but the approved use is limited to descriptive review rather than operational automation. The malformed timestamp, blank energy value, repeated line-hour, excessive downtime, shift mismatch, and high temperature must be visible to the supervisor; those issues rule out stronger claims.

## Conditions

| Condition | Owner | Evidence that closes it | Review trigger |
|---|---|---|---|
| Reconcile CSV lines 19, 47, 54, 60, 63, and 74 with source records | Data owner | Source comparison recorded | Before the next handover |
| Review the 112.3 C reading at CSV line 6 | Controls team | Calibrated sensor or maintenance note | Before any intervention |

## Known issues I am accepting

List what stays broken after approval, and why the permitted use survives it.

| Issue | Why the permitted use survives it |
|---|---|
| One timestamp is not in the contracted format | Descriptive review can proceed only with the warning shown |
| One energy value is blank and one line-hour is duplicated | Output and downtime can still be discussed with those records excluded or reconciled |
| Downtime, shift, and temperature records fail review rules | They are flagged for human review, not treated as confirmed failures |

## Record

- Decided by: Syed Muhammad Qasim Zaidi
- Date: 2026-10-07
- Dataset fingerprint: `9fd52cb5dad2e8f74ec2fd6827f93a819b43b6ceb4c36cc53cdc4709c190235d`
- Commit: working tree checkpoint
