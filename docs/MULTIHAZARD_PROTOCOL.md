# Multi-hazard forecast and action-workbench protocol

Defined before fitting this extension. Earlier versions already explored this historical snapshot; this is not an independent preregistration.

## Forecast targets

Evaluate each of four operational weather labels over the next 3 and 7 complete calendar days, excluding the issue day:

- Rain accumulation: total ≥20 mm over 3 days, or ≥40 mm over 7 days.
- Heat exposure: at least one daily maximum air temperature ≥30 °C.
- Low rainfall: total rainfall below the horizon length in mm (mean <1 mm/day).
- Hot and dry: heat exposure AND low rainfall within the same future window.

These are weather-label definitions, not measured runoff, river flow, drought, water temperature, dissolved oxygen, pollution or ecological damage. The compound label is fitted directly; probabilities of separate events are not multiplied.

## Chronology and missing data

One row per exact weather group and issue date. Require all ten weather fields for the previous seven days including issue day, and all future rainfall/maximum-temperature labels within the target window. A target window must lie entirely within a split: train 2023–2024, validate 2025, test 2026 through September 21. Windows spanning split boundaries are excluded. No interpolation or duplicate site-level weather rows.

Features: issue-day ten fields; previous-day rainfall; log rainfall; 3- and 7-day rainfall; 3- and 7-day mean temperature; 7-day maximum temperature; 3- and 7-day relative humidity; 1-day pressure change; 3-day pressure change; temperature change; 7-day maximum wind; sine/cosine of future-window start month/day on a 366-day calendar. Features contain no future observation, health label or site identifier.

## Comparison and selection

Fit two fixed candidates: standardized L2 logistic regression (C=0.1) and histogram gradient boosting (100 iterations, learning rate 0.06, 15 leaves, minimum 40 samples per leaf, L2=2, no automatic early stopping). Select the lowest 2025 Brier score. Scaling and fitting use training rows only; no refit on validation. Compare with a same-group seasonal training-frequency baseline and a persistence-state baseline (training-smoothed future event frequency conditional on whether the preceding same-length observed window met the label). Each strategy's F1 decision threshold is selected on validation only.

Report every task, both candidate metrics, seasonal and persistence baselines, prevalence, discrimination, Brier score, precision/recall, confusion counts, threshold sensitivity, monthly results and reliability-bin counts. Export every frozen test probability. Poor results remain visible. A 7-calendar-day moving-block bootstrap gives descriptive uncertainty for seasonal-minus-selected Brier, all groups kept together, 300 resamples, seed 42. Overlapping target windows increase dependence.

## Geographic stress test

For the 3-day rain target, hold out each entire city in turn. Fit the two fixed candidates on other cities' 2023–2024 rows; choose the candidate on other cities' 2025 rows; evaluate the held-out city in 2026. The transferable baseline pools training labels from other cities within ±30 calendar days. There is no held-out-city label in fitting, model selection or baseline construction. This is an exploratory same-dataset geographic stress test, not independent external validation.

## Decision layer

Default ordering is forecast probability. An optional context-weighted priority index is `100 × p × (1 + w × urban_fraction)` with user-selected w in {0,0.25,0.5,1}. Urban fraction is source artificial/urban cover only when explicitly available; absent context contributes no uplift and is flagged. It is a transparent planning preference, not a calibrated ecological risk probability or catchment runoff estimate. The model probability does not change. One-per-weather-group selection is optional; no travel optimization is claimed.

Field checklists are analyst-authored measurement suggestions grounded in general EPA/USGS mechanisms. They are not validated site-specific prescriptions. Local observations are user-entered records and do not update models or become official source data. Saved plans and reports retain issue date, future target window, label definition, probability, historical outcomes, and chosen priority rule.
