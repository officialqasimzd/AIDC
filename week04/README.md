# Week 4 Lab: Reproducible Project Architecture and Repository Hygiene

Last week you wrote checks that find faults in a file. This week you find out
whether anybody but you can run them.

The work you are restructuring is **your own Week 3 work**, from your Week 3
assignment repository. This Week 4 repository is where the restructured
version lives.

**This lab is not marked.** It is practice for something that will be: the
capstone repository is read against exactly the checklist you complete today.

## Choose a partner, then one folder each

Week 4 is a Classroom 50 group assignment for **pairs, and you choose your own
partner**. Agree it between you before you accept. One of you accepts the
assignment and creates the group, then adds the other by their GitHub
username; the other accepts and joins it. You then share one repository.

If the numbers leave someone over, make a group of three, and run Part F as a
round: each of you runs the next person's folder.

Inside the repository, each of you works in **a folder named after your own
GitHub username**, and nobody touches the other's folder until Part F. Your
folder and your two documents are yours alone, whoever your partner is.

```text
<repository root>
├── README.md                 this guide
├── src/check_repo.py         the auditor, shared
├── tests/test_check_repo.py  its tests, shared
├── docs/                     blank templates to copy
├── ahmad-r/                  one partner's restructured Week 3 work
└── fatima-k/                 the other's
```

The reason for pairs is Part F: you run each other's work cold, and a private
individual repository cannot be cloned by anyone but you. Sharing one
repository is what makes the handover real.

## Three rules

1. **Report, do not repair.** When you run a partner's folder, you write down
   what happened. You do not fix it for them. Same rule as Week 3.
2. **An empty folder or it did not happen.** "It works on my machine" is the
   claim under test, so the test cannot be run on your machine in the folder
   you have been working in.
3. **Never commit a credential.** Not temporarily, not to make something run,
   not in a branch you plan to delete. There is no undo. If it happens, say so
   immediately and rotate the credential; you will not be penalised for
   reporting it, and the alternative is much worse.

## Sequence (120 minutes)

| Part | Minutes | What you do |
|---|---:|---|
| A. Audit what you already have | 15 | Set up, clone your Week 3 repo alongside, run the auditor against it, record the failures |
| B. Restructure | 25 | Move your Week 3 work into the skeleton, inside your own folder, and isolate every path |
| C. Pin and document | 20 | Exact versions, a README with one command that works |
| D. Make the tests pass | 30 | Write the three missing checks in `src/check_repo.py` until `pytest -q` is green |
| E. The cold clone | 15 | Clone this repository into an empty folder and run your own work |
| F. Swap | 15 | Run your partner's folder cold, complete the handover report |

### A. Audit what you already have

Clone this repository once, open it in VS Code, and from its root create the
environment and install:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux the activate line is `source .venv/bin/activate`.

Now clone your **Week 3 assignment repository** beside this one, so the two
sit as siblings, and point the auditor at it before you change anything:

```bash
git clone <your-week-3-repository-URL> ../week03
python src/check_repo.py --repo ../week03 --output artifacts/audit_before.json
```

Three checks are written; three are not yet, and report as failures with a
reason. That is expected, and you write them in Part D.

Keep `artifacts/audit_before.json`. The difference between before and after is
the clearest record you will have of what you actually changed.

### B. Restructure

Create a folder named after your GitHub username at the root of this
repository, and build the skeleton from the lecture inside it:

```text
<your-username>/
├── data/raw/          never edited, never overwritten
├── data/processed/    derived, and rebuildable from raw
├── src/               code that can be imported and tested
├── tests/             the checks run without you
├── docs/              decisions, in writing
└── artifacts/         generated, never hand-edited
```

Move your Week 3 work into it: the validator into `src/`, its tests into
`tests/`, your data file into `data/raw/`, your reports into `docs/`. Copy the
two templates from this repository's `docs/` into your own `docs/` as well;
you complete those in Parts E and F.

Then remove every absolute path. `src/paths.py` in this repository is the
worked example: one module that derives everything from the folder it lives
in, with an environment-variable override for anything that genuinely has to
vary. Copy the idea into your own `src/`. Run it to see what it resolves to:

```bash
python src/paths.py
```

The test is not whether the paths look tidy. It is whether your folder still
works when it is cloned to a machine that has never seen it.

### C. Pin and document

Pin every dependency to an exact version. `pip freeze` will tell you what you
actually have:

```bash
python -m pip freeze
```

Take the packages your validator imports and pin those in your own folder's
`requirements.txt`; you do not need every transitive dependency by hand.

Then write `<your-username>/README.md`. It needs, at minimum, what the project
does, where the data came from and under what licence, and **one command that
runs it**, in a fenced block. The auditor checks for the fenced block; your
partner checks whether the command works.

### D. Make the tests pass

Three checks in `src/check_repo.py` at the repository root are marked TODO.
Seven tests fail because of them:

```bash
pytest -q
```

The auditor is shared, so **agree with your partner who writes which check**
before either of you starts, and commit after each one. Two people editing
the same function at the same time is how you meet slide 17 for real.

Each docstring says what the check has to decide and what evidence it should
give back when it fails. Follow the shape of the three worked examples: a
check returns a `Result`, it never repairs anything, and its evidence names
files and line numbers rather than saying something is wrong somewhere.

Two of the failing tests exist to catch the lazy version of the rule: a
`tests/` folder containing no actual test, and a `.gitignore` that lists the
right patterns while the secret sits in the repository anyway.

Then run the finished auditor against your own folder:

```bash
python src/check_repo.py --repo <your-username> --output artifacts/audit_after_<your-username>.json
```

### E. The cold clone

This is the part that decides whether any of the rest is true.

```bash
cd /some/empty/folder
git clone <this-repository-URL> cold
cd cold/<your-username>
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Then run it, following only your own README. Not the folder you have been
working in, which has your environment already active and an afternoon of
half-finished state. An empty folder, on a path you have never used.

Most of you will fail this the first time. That is the exercise, not a problem
with it. Record every failure in your own
`<your-username>/docs/reproducibility_checklist.md` under "What broke the
first time", including the ones you fixed in thirty seconds.

### F. Swap

In the same cold clone, move into your **partner's** folder and follow their
README exactly. Do not ask them anything until you are properly stuck, and
write down every question you do have to ask, in your own
`<your-username>/docs/handover_report.md`.

Then run the auditor against their folder and paste the output into the
report:

```bash
python src/check_repo.py --repo <partner-username>
```

You may read anything in their folder. You may not change anything in it.

## Where every file is, and what it is for

| Path | What it is | What you do with it |
|---|---|---|
| `README.md` | This guide | Follow it in order |
| `requirements.txt` | This repository's environment, pinned exactly | Install it; copy the style into your own folder |
| `.gitignore` | A worked example, with the reasons in comments | Read the comments; adapt it inside your own folder |
| `src/check_repo.py` | The auditor: three checks written, three TODO | Write the three in Part D, shared with your partner |
| `src/paths.py` | The worked example of isolating paths | Read it, run it, copy the idea |
| `tests/test_check_repo.py` | Thirteen tests, seven failing | Make them pass; do not edit them |
| `docs/reproducibility_checklist.md` | Blank checklist | Copy into your own `docs/` and complete it about **your** folder |
| `docs/handover_report.md` | Blank Part F | Copy into your own `docs/` and complete it about **your partner's** folder |
| `artifacts/` | Audit output | `audit_before.json` and one `audit_after_<username>.json` each |
| `<your-username>/` | Your restructured Week 3 work | Everything in Parts B, C and E |

## What to push, if you want feedback

Nothing in this lab is marked, and nothing has to be pushed. If you want
feedback on your work, push your own folder and your own two documents. You
do not need your partner's agreement to do that, and you do not push theirs:
each of you hands in individually, or not at all.

A complete piece of work, for your own folder, is:

1. `<your-username>/`, with the skeleton, an exactly pinned
   `requirements.txt`, a README containing a command that works, and an
   active `.gitignore`;
2. `<your-username>/docs/reproducibility_checklist.md`, completed with
   evidence;
3. `<your-username>/docs/handover_report.md`, completed about your partner's
   folder;
4. `artifacts/audit_after_<your-username>.json`.

The auditor in `src/check_repo.py` is shared, so it only needs pushing once,
by whichever of you finishes it.

## What a good outcome looks like

Not a clean first attempt. A cold clone that failed three times and is written
up precisely is a better outcome than one that reportedly worked immediately,
because the second tells you nothing about whether you understood why. The
same goes for the handover report: four questions described exactly are worth
more than an empty table you had to help each other through.

Because the capstone repository is read against this same checklist, the most
useful thing you can take from today is a list of what broke, in your own
words, while it is still cheap to find out.

## Before you push

This repository has two of you pushing to it. Pull before you push, every
time:

```bash
git pull
git status
```

If the pull reports a conflict, that is slide 17. Read both sides, decide,
remove all three marker lines, run `pytest -q`, then commit.

Check, every time, that `git status` is not about to commit `.venv/`, a data
file you do not have the licence to redistribute, or anything holding a
credential. If it lists hundreds of files, your `.gitignore` is not doing its
job yet, and that is a finding for your checklist rather than something to
push and tidy later.
