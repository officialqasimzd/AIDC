# Handover report

You run a partner's repository cold. They run yours. Neither of you explains
anything until the other has stopped.

This document records what happened when **you ran their folder**, in the same
cold clone of the shared repository. Your partner writes the matching one
about yours. Keep it in `<your-username>/docs/`.

## Ground rules

1. **Do exactly what the README says.** Not what you would have done. If the
   README is wrong, that is the finding.
2. **Do not ask until you are stuck.** Every question you have to ask is a
   thing that was living in their head instead of in the repository. That is
   the measurement, so record it rather than working around it.
3. **Report, do not repair.** Do not fix their repository. Write down what
   happened and hand it back. The same rule as Week 3.

## Whose repository

| | |
|---|---|
| Partner's GitHub username | |
| Partner's folder in the shared repository | |
| Commit you cloned (`git log -1 --oneline`) | |
| Operating system you ran it on | |

## Every question you had to ask

One row per question, in the order they came up. An empty table is a strong
result and a rare one; an honest table of four is worth more than an empty one
you had to help along.

| # | What you had to ask | What you were trying to do | What should have made it unnecessary |
|---:|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

## Did you get their number?

```text
Command you ran:

What it produced:

Does it match what their report claims:
```

If it does not match, say so plainly and give both figures. A mismatch between
two runs of the same code is the single most useful thing this exercise can
turn up, and it is not a criticism of your partner.

## The audit

Paste the output of the auditor run against their repository:

```bash
python src/check_repo.py --repo <partner-username>
```

```text

```

## One sentence back to them

The most useful thing they could change, and why. Be specific and be kind:
you are describing a repository, not a person, and yours is being read the
same way right now.
