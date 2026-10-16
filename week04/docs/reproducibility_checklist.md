# Reproducibility checklist

Copy this into `<your-username>/docs/` and complete it there, about **your own
folder**, not about the shared repository as a whole.

Answer each check with **Yes**, **Partly** or **No**, and give the evidence: a
file path, a command, or a line number. "I was careful about it" is not
evidence. The point of the right-hand column is that somebody else can verify
your answer without asking you anything.

| Check | The question it asks | Yes / Partly / No | Evidence in the repository |
|---|---|---|---|
| Environment | Can the software be reinstalled exactly? |  |  |
| Entry point | Is it obvious what to run? |  |  |
| Paths | Does it run from a fresh clone, in a folder it has never seen? |  |  |
| Data | Is the source and licence recorded? |  |  |
| Secrets | Is anything private committed, now or in the history? |  |  |
| Tests | Does anything check it without you? |  |  |

## The cold-clone result

This is the part that decides whether the rest is true. Clone your own
repository into an empty folder on a path you have never used, create a fresh
environment, and run it.

```text
Command I ran:

What happened:

Attempt on which it worked (1st, 2nd, 3rd):
```

## What broke the first time

List everything that failed on the cold clone, even if you fixed it in thirty
seconds. This section is worth more than a clean first attempt, because
a repository that works first time tells me nothing about whether you
understood why.

| What broke | Why it broke | What you changed |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |

## The one thing still in your head

Name one thing a stranger would still have to ask you. Everybody has one. If
you genuinely cannot find one, say what you checked in order to be sure.

Write 60 to 100 words.
