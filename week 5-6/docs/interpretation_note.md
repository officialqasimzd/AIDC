# Interpretation note

One page. Six questions, each answered in one sentence, each sentence backed
by something a reader can check in this repository. This is the first
of the lab's two deliverables, and the same six questions are how the capstone
model will be read.

Your file: `data/raw/shift_week_<username>.csv`
SHA-256: 

## 1. What does it predict?

Name the target column and the unit. Say for whom the number is produced and
when it is needed.

## 2. What does it beat, and by how much?

The incumbent rule is "next hour looks like this one". Give both scores, on
the same test hours, with the same metric, and the difference in kWh.

| Model | Average miss, kWh | Hours short | Hours scored |
|---|---:|---:|---:|
| Naive, last hour (the rule) |  |  |  |
| Line mean |  |  |  |
| Same hour yesterday |  |  |  |
| Regression |  |  |  |

Paste the table `scorecard()` prints, then write the sentence.

## 3. On which metric, and on which does it lose?

Average miss is one metric. Hours short is another, and they do not have to
agree. Say plainly where your model wins and where it does not.

## 4. What did it miss?

Every baseline missed the same hour. Name it, give its residual for the rule
and for your regression, and give the reason. If you do not know the reason,
say who could tell you, as you did in Week 3.

## 5. What must be known at the top of the hour?

List every feature your regression uses and, for each, why it exists when the
prediction is made. Then name the column in the file that fails that test,
and how you knew.

| Feature | Known at the top of the hour because |
|---|---|
|  |  |
|  |  |

The column that fails the test: 

## 6. Should it replace the rule?

A recommendation, not a score. If it beats the rule by two kWh an hour, is
that worth changing how the plant plans energy? Say what changing would cost,
and decide.

## The sentence

Write the finding in one line, with a number, a comparison, a unit, a metric
and a period. It should sound like: *it beats the rule by X kWh an hour on the
last two days, by mean absolute error.*
