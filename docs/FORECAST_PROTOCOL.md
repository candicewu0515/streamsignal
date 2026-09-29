# Next-day rainfall experiment — protocol

Defined before fitting the first forecasting model in this revision.

## Question

Can a small, inspectable model improve on a seasonal training-data baseline when predicting whether the **next calendar day's recorded rainfall is at least 10 mm**? This is a weather-label experiment, not pollution or disease prediction. The 10 mm cutoff is an operational label definition, not an official warning threshold.

## Unit and observation timing

One exact weather group and one target calendar day. Use the 21 distinct series rather than treating 106 duplicated site series as independent observations. Predictors are assumed available after the issue day's complete daily observation. The target is the following day's recorded rainfall. This is a retrospective hindcast; original data publication latency and revision history are unknown.

## Temporal splits

Assign rows by **target date**, not issue date:

- Training: 2023-01-01 through 2024-12-31, subject to predictor availability.
- Validation: 2025-01-01 through 2025-12-31.
- Locked test: 2026-01-01 through 2026-09-21.

Require all ten weather fields for the issue day and previous two calendar days, plus an observed target. Exclude incomplete windows; do not fill missing weather. Earlier observed days may be used to predict across a split boundary, because they would already be known. No test target is used for preprocessing, fitting, hyperparameter selection or decision-threshold selection.

## Features fixed before fitting

- Issue-day temperature mean/minimum/maximum, humidity, precipitation, mean/max wind, surface pressure, cloud cover and solar radiation.
- Log(1 + issue-day rainfall).
- Rainfall one day earlier and trailing three-day rainfall.
- Trailing three-day mean temperature and humidity.
- One-day pressure change.
- Sine and cosine of target day-of-year on a 366-day calendar.

No future weather, health labels, group identifiers or outcome-derived feature selection is used. Only training rows determine standardization means and scales.

## Models and selection

- Logistic regression with L2 regularization; candidate C values 0.01, 0.1, 1 and 10. Select the lowest validation Brier score, breaking ties toward the smaller C. Do not refit on validation data.
- Seasonal baseline: same-group training target labels within ±30 calendar days, with Beta(1,1) smoothing.
- Constant baseline: overall training event frequency.

For each strategy, select the F1-maximizing decision threshold on validation probabilities, breaking ties toward the higher threshold. The test uses those frozen thresholds. F1 selection is a demonstration rule, not a stakeholder-calibrated action policy.

## Reported outputs

Test event frequency, Brier score, Brier skill relative to the seasonal baseline, ROC AUC, average precision, precision, recall, F1 and confusion counts. Include validation results, chosen parameters, reliability bins, monthly test results, all test predictions, standardized coefficients and a data-split audit.

Also compute a 95% descriptive moving-block-bootstrap interval for the **seasonal-baseline Brier minus model Brier** difference: 7-calendar-day blocks, all groups kept together per day, 300 resamples, fixed seed 42. This accounts for some short-term temporal and same-day spatial dependence; it does not establish transportability or eliminate all dependence.

## Interpretation limits

The same weather regions occur in training and testing. The test is temporal, not an unseen-region evaluation or a prospective trial. Source weather may be gridded or postprocessed; provenance has not been fully verified. No weather-service benchmark or live operational deployment is claimed. Report failure to improve if it occurs; do not change the model after viewing test results to obtain a more favourable headline.
