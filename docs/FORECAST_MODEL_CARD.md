# Next-day rainfall model card

## Intended use

An inspectable research experiment for the Resilience Informatics prototype. Predict whether the next calendar day's **recorded rainfall is at least 10 mm** using only weather through the issue day. The 10 mm threshold is a task definition, not an official warning category. This is not a pollution, disease, river-flow or water-safety model.

## Data and chronology

OneAquaHealth weather snapshot; 106 sites reduced to 21 exact ten-field time series. Different series may remain correlated. Each row is a weather-group/target-day pair. The issue day and two preceding days require all ten weather fields; target rainfall must be observed. Missing values are not imputed.

| Split, by target date | Rows | Events | Event rate |
|---|---:|---:|---:|
| Train: 2023-01-04–2024-12-31 | 15,288 | 1,341 | 8.77% |
| Validation: calendar 2025 | 7,665 | 611 | 7.97% |
| Test: 2026-01-01–2026-09-21 | 5,376 | 394 | 7.33% |

Target dates around the two global missing dates remove eight target days from the 2026 evaluation: August 4–7 and August 27–30. The first three calendar days of the whole snapshot cannot provide the required feature history. Features may cross a year boundary, but target labels determine split membership.

The experiment protocol was written before fitting this model, within development of an already explored historical snapshot. It is a development-time temporal holdout, not an external preregistration or independent prospective test.

## Model and selection

18 features: the ten issue-day fields, log-transformed issue-day rain, previous-day rain, three-day rain, three-day mean temperature and humidity, pressure change, and sine/cosine of the target calendar date. No future weather, site identity or health label enters the model.

A training-fitted StandardScaler feeds L2 logistic regression. Four regularization candidates (C=0.01, 0.1, 1, 10) were compared by validation Brier score. Selected C=0.01. The model was not refitted on validation data. Each strategy's threshold maximizes validation F1, with ties resolved toward the higher threshold. The model threshold is 17.0978%. No model change was made to improve the test result after inspection.

Comparators: training event frequency and same-group seasonal training frequency within ±30 calendar days, smoothed with Beta(1,1). All strategies are evaluated on identical test rows.

## Frozen 2026 results

| Metric | Logistic model | Seasonal baseline | Constant baseline |
|---|---:|---:|---:|
| Brier score (lower better) | 0.0570 | 0.0677 | 0.0681 |
| ROC AUC | 0.8540 | 0.6489 | 0.5000 |
| Average precision | 0.3717 | 0.1063 | 0.0733 |
| Precision | 0.3145 | 0.1289 | 0.0733 |
| Recall | 0.4797 | 0.3274 | 1.0000 |
| F1 | 0.3799 | 0.1849 | 0.1366 |

Relative Brier skill versus seasonal baseline is **15.85%**. Absolute baseline-minus-model Brier difference is 0.010728, with a descriptive 95% moving-block bootstrap interval [0.006413, 0.016251]. The bootstrap uses 300 seven-calendar-day block resamples, seed 42, retaining all groups within each sampled date. It does not address new-region generalization or all sources of dependence.

At the frozen decision threshold: 189 true positives, 412 false positives, 205 false negatives and 4,570 true negatives. **52.0% of observed events are missed**, and most flagged rows are not events. Better aggregate probability error does not make this an operational warning system.

## Limitations

- Training and testing use the same regions and exact-series groups; no geographic holdout was performed.
- Source weather product, sensor/grid resolution and publication latency are unverified. Completed daily aggregates may not be available at a practical issue time.
- Two training years and one validation year are short; shifts in climate, season or source processing may degrade results.
- Correlated groups and consecutive days mean 5,376 rows are not 5,376 independent cases.
- Sparse high-probability reliability bins are unstable; counts are included in the app and JSON.
- Standardized coefficients are predictive associations, not causal effects.
- No feature ablation, complex-model comparison or prospective intervention trial is claimed.

## Reproducibility and provenance

Protocol: `FORECAST_PROTOCOL.md`. Script: `tools/train_forecast.py`. Exact runtime dependencies: `tools/requirements-model.txt`. Source hashes: `data/audit.json`. All coefficients, scaler parameters, candidates and metrics: `results/forecast_metrics.json`. Every test prediction: `results/forecast_test_predictions.csv`. The bundled Python tests independently reconstruct exported probabilities and metrics and check feature chronology and missingness.

Method references: [scikit-learn LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), [Pipeline](https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html), [model evaluation metrics](https://scikit-learn.org/stable/api/sklearn.metrics.html).
