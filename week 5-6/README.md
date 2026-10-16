# Weeks 5 and 6 Lab: Baseline Modelling, Uncertainty and Limitations

The lectures were about bread. The lab is about your plant. Same method, a
different target, and your own file.

You predict **next hour's energy for each production line**. The plant already
has a rule for that, the same one the manager had for bread: assume next hour
looks like this one. Your job is to measure that rule, build three baselines
and one regression, improve the regression by one feature, measure how far it
can be trusted, and say what margin the plant should book with.

This is an **individual, marked** Classroom 50 assignment, covering the Week 5
and Week 6 labs in one. Accept it, clone it once, and work in it directly.

## Why not predict failures?

Because your file has none. You proved that in Week 3: no verified failure,
inspection or maintenance outcome anywhere in it. A prediction of something
that was never recorded cannot be scored, so it cannot be a model. Energy is
in the file every hour, for every line, so it can.

## The booking

At the top of each hour the plant books next hour's energy with its supplier.
Energy used beyond the booking is bought at the imbalance price; energy booked
and not used is paid for anyway. In this lab a kWh short costs three times a
kWh over. The ratio is illustrative and is set once, as `PRICE_SHORT` and
`PRICE_OVER` at the top of `src/uncertainty.py`. In the lecture's notation these
are $C_u$ and $C_o$.

That gives the model a decision to support, and a way to say whether it is
good enough: what does booking by its numbers cost, against booking by the
rule?

## Five rules

1. **Measure the rule first.** Before you fit anything, score "next hour looks
   like this one". That number is the bar. Write it down before you build.
2. **Same hours, same metric.** Every model is scored on the same test hours
   with the same function, and every booking is costed on the same hours at the
   same prices. A model scored on different hours from the rule has not been
   compared with it.
3. **A feature has to exist at the top of the hour.** If the number would not
   be known when the prediction is made, it is not a feature. It is a leak,
   and there is one in your file.
4. **Fit on the training days, judge on the test days.** $s$, the streak check,
   the sensitivity ranges and the margin all come from the training hours, 12 to
   17 January. The test hours, 18 January and the early hours of the 19th, are
   only for checking them. A margin chosen by looking at the test hours has not
   been tested.
5. **Say the count, and name the range.** Every range in the notes comes with
   what it rests on, how many hours and how many days, and with its proper
   name: a coverage check, a sensitivity range or a margin. None of the ranges
   in this lab is a formal 95% confidence interval.

## Sequence (one session of 120 minutes, notes afterwards)

| Part | Minutes | What you do |
|---|---:|---|
| A. Generate and score the rule | 10 | Make your week of data, record its fingerprint, score the incumbent rule |
| B. Three baselines, by hand then in code | 30 | Six rows with a pencil, then the three missing functions in `src/baselines.py` |
| C. Regression, and the leak | 25 | Two or three features that pass the top-of-the-hour test; name the column that leaks |
| D. The uncertainty functions | 25 | The three missing functions in `src/uncertainty.py` until `pytest -q` is green |
| E. How sure can you be? | 15 | Add one feature; $s$, coverage, streaks, sensitivity ranges, the hour every model missed |
| F. Book with a margin | 10 | A margin from the price, chosen on training hours, costed on test hours |
| G. The two notes, and push | after the session | Two one-page notes, each sentence backed by a number |

Parts A to F fit the session if you keep moving. Push whatever you have before
you leave; the two notes are completed afterwards, by the deadline on the
assignment.

### A. Generate and score the rule

Open the repository in VS Code, create the environment, and install. Use
Python 3.12 or 3.13; the pinned versions install on both.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux the activate line is `source .venv/bin/activate`.

Generate your file. Seven days, three lines, one row per line per hour, in the
Week 3 columns plus one:

```bash
python src/make_week.py --student-id your-github-username
```

Record the SHA-256 it prints at the top of `docs/interpretation_note.md`, as
you did in Week 3. Your file is yours: the same username always produces the
same file, and nobody else's matches it.

Then open `notebooks/week5_6_baselines_uncertainty.ipynb`, set `STUDENT`, and
run the first two code cells. They load your file, attach next hour's energy
as the target, split the last two days off as the test set, and score the
incumbent rule. **Write that number down before you do anything else.**
Everything you build is compared with it.

### B. Three baselines, by hand then in code

The notebook shows six consecutive hours of one line. For those six rows, fill
in the three baseline predictions with a pencil, and work out the average miss
for each. You are doing this by hand once so that when a function returns a
number you know what it did.

Then write the three functions in `src/baselines.py` marked TODO:

```bash
pytest -q tests/test_baselines.py
```

Write them one at a time and re-run. `same_hour_yesterday` is mostly an
alignment problem, and the docstring tells you the trap. `mean_absolute_error`
must ignore missing pairs rather than count them as zero. `fit_regression`
builds a design matrix with a column of ones and hands the arithmetic to
`numpy.linalg.lstsq`; the docstring says exactly what to return so that
`predict` can use it. When the six tests pass, run the check cell under the
by-hand table.

### C. Regression, and the leak

Choose two or three features. Every one must pass the top-of-the-hour test:
at the moment next hour's prediction is made, is this number known? The
notebook lists candidates, and `passes_top_of_hour_test` in `src/baselines.py`
holds the course's answer for each, but the argument is yours to make in the
note. Fit, predict on the test hours, and read the scorecard.

One column in your file will not exist at the top of the hour. It is not
labelled, and it will make a regression look superb. Find it, say how you
knew, and do not use it.

Then look at the hour every model missed. There is one, and you have met it
before.

### D. The uncertainty functions

Three functions in `src/uncertainty.py` are marked TODO. Once Part B is done,
exactly six tests fail, because of them:

```bash
pytest -q
```

`residual_spread` is the lecture's $s$: check it reproduces 3.58 from the six
promotions. `lag1_autocorrelation` must pair each hour with the one before it
**in the same line**; the docstring says why. `margin_for_price` is one
quantile, and the docstring says which. All 26 tests should be green before
Part E.

### E. How sure can you be?

Add **one** feature to your Part C regression, passing the same test, and score
the improved model on the same test hours. A legitimate feature does not have
to help; if yours does not, say so in the note and try another.

Then run the rest of Part E. It gives, for every model, $s$ on the training
hours, the lag-1 autocorrelation of the misses, and the share of test hours
that landed within $\hat y \pm 1.96\,s$. With residuals $e_i = y_i - \hat y_i$
and $p$ numbers fitted,

$$s = \sqrt{\frac{\sum_i e_i^2}{n - p}}.$$

$\hat y \pm 1.96\,s$ is a nominal range built on a normal reference: it would
hold about 95% of hours if the misses were independent, normally distributed,
equally spread at all times, and $s$ were known exactly. The share of test
hours inside it is an **empirical coverage** check of how well the range held
on hours the model never saw. It is not a guaranteed 95% prediction interval,
and streaks, skewed or heavy-tailed misses, a spread that changes between day
and night, and the uncertainty in $s$ itself can all move it away from 95%.

One of the four models has misses that run in streaks. Work out which, and
why the others do not: what does a model that knows this hour's energy know
that one model does not?

Then the spread before day hours against night hours, and each coefficient
refitted with each training day left out in turn. The lowest and highest values
across those refits are the coefficient's **leave-one-day-out sensitivity
range**: how much it depends on which days you happened to have. It is a
sensitivity check, and it is not a 95% confidence interval. Finally, the hour
every model missed, against the range. Name it and say who could explain it;
working out why models fail, hour by hour, is Week 7.

### F. Book with a margin

Every model books $q = \hat y + m$, with a margin $m$ from its own training
residuals $e = y - \hat y$, chosen so that

$$F_e(m) = \frac{C_u}{C_u + C_o} = \frac{3}{3 + 1} = 0.75,$$

where $C_u$ is the cost of a kWh short and $C_o$ of a kWh over. Every booking is
costed on the test hours. Compare your model's booking with the rule's
booking, both with margins. Then look at how the margin moves when the price
changes.

### G. The two notes, and push

Complete `docs/interpretation_note.md` (Parts A to C) and
`docs/uncertainty_note.md` (Parts E and F). Six questions each, one sentence
each, each backed by a number in `artifacts/` or a table the notebook printed.
Then:

```bash
git status
git add src/ tests/ docs/ notebooks/ artifacts/scorecard.csv artifacts/spread.csv artifacts/booking_scorecard.csv data/raw/
git commit -m "Complete Weeks 5 and 6 baseline and uncertainty checkpoint"
git push
```

Do not commit `.venv`, notebook checkpoints, or caches.

## Where every file is, and what it is for

| Path | What it is | What you do with it |
|---|---|---|
| `README.md` | This guide | Follow it in order |
| `requirements.txt` | The environment, pinned exactly | Install it; do not edit it |
| `src/make_week.py` | Generates your week of data from your username | Run it once in Part A |
| `src/paths.py` | Where files live, derived from the repository root | Import it; never type a path |
| `src/baselines.py` | Loading, target, split, three baselines, scoring; three TODOs | Write the three in Part B |
| `src/uncertainty.py` | Features, residuals, refits, booking costs; three TODOs | Write the three in Part D |
| `tests/test_baselines.py` | Fourteen tests, six failing | Make them pass; do not edit them |
| `tests/test_uncertainty.py` | Twelve tests; eight fail until Part B is done, six until Part D | Make them pass; do not edit them |
| `notebooks/week5_6_baselines_uncertainty.ipynb` | Parts A to F | Run it in order |
| `docs/interpretation_note.md` | The first deliverable | Complete it in Part G |
| `docs/uncertainty_note.md` | The second deliverable | Complete it in Part G |
| `data/raw/` | Your generated file | Never edit it |
| `artifacts/` | The three tables the notebook writes | Generated; commit those three |

## What you submit

1. `data/raw/shift_week_<username>.csv`, unedited, with its SHA-256 in the interpretation note;
2. `src/baselines.py` and `src/uncertainty.py` with all six functions written, `pytest -q` green;
3. the executed `notebooks/week5_6_baselines_uncertainty.ipynb`, including the by-hand table and your chosen features;
4. `artifacts/scorecard.csv`, `artifacts/spread.csv` and `artifacts/booking_scorecard.csv`;
5. `docs/interpretation_note.md` and `docs/uncertainty_note.md`, all twelve questions answered, each with its sentence.

## How this is marked

| Weight | What earns it |
|---:|---|
| 30% | The six functions are correct: alignment, missing values, the column of ones, the $n - p$ denominator, pairing within a line, the right quantile |
| 15% | The regression uses only features that pass the top-of-the-hour test, and the leak is named with a reason |
| 10% | The scorecard and the booking scorecard compare every model on the same hours with the same metric and prices, and the notes say where the model loses as well as wins |
| 10% | The coefficient is read as a measurement, with its leave-one-day-out sensitivity range, named as such, and the days it rests on |
| 10% | The coverage, streak and spread checks are reported with their numbers and correct names, and the model whose misses run in streaks is named with the reason |
| 10% | The margin is chosen on training hours and costed on test hours against the rule with its own margin, and the share of hours short is compared with the aim |
| 5% | The missed hour is identified, its residual given, and its reason stated or its owner named |
| 10% | The untestable assumption is stated precisely, the raw file is unchanged with its fingerprint recorded, and the repository is clean |

You are not marked on beating the rule, or on your model's cost being lowest.
A regression that loses to "next hour looks like this one", reported honestly
with the reason, scores higher than one that wins by leaking or by choosing
its margin on the test hours.

## Before you push

```bash
git status
```

Check that you are not about to commit `.venv/`, checkpoints, or anything you
generated other than the three tables in `artifacts/`.
