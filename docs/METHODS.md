# StreamSignal — methods and limitations

## Purpose and intended user

StreamSignal is a retrospective weather-screening and field-planning prototype for an environmental analyst reviewing urban water research sites. It helps decide where additional human review might be useful. It does not establish pollution, pathogen exposure, illness, drought status, or water safety. It is not an operational early-warning system.

## Source snapshot

The OneAquaHealth Resilience Map data service was downloaded on 2026-09-28, America/Chicago. The snapshot includes 106 sites, 143,948 daily weather rows, 96 health-risk samples, 100 nitrate-indicator records and 104 urban-context records. Weather observations span 2023-01-01 to 2026-09-21. Historical health samples span 2023–2024, usually one sample per covered site. These labels do not support a well-validated temporal health-prediction model.

The exact source CSV SHA-256 hashes are in `data/audit.json`. The original full CSV/JSON files are in the separately delivered OneAquaHealth research data package.

## Weather groups

Sites are grouped by exact equality across every date and all ten downloaded weather fields. This yields 21 unique time series. Group numbers are deterministic identifiers within this build, not provider grid IDs. Equality is evidence of repeated information; it does not by itself identify a sensor, grid resolution, or upstream product. Different series are not necessarily statistically independent either.

The app stores one copy of each distinct series and links each site to its group. This reduces payload size without losing numeric observations. Sites still retain their own coordinates, health records and urban context.

## Date handling and missingness

All source dates are treated as calendar dates without timezone shifts. Data are aligned to a complete daily calendar. The source is missing all sites on 2026-08-04 and 2026-08-27. The payload explicitly inserts null rows for these dates; values are never filled with zero or interpolated.

The dry-run state starts unknown at the left boundary until an observed wet day. A missing rainfall observation resets the state to unknown. Subsequent dry days remain unknown until an observed day with at least 1 mm rainfall makes the counter zero. This conservatively avoids inventing the length of a dry spell across a gap.

## Signals

1. **Rainfall:** selected-day precipitation plus the two preceding calendar days, in mm. Requires all three observations. The sum is rounded to two decimal places to avoid floating-point tie artifacts in source data recorded to hundredths.
2. **Heat:** selected-day maximum 2 m air temperature, in degrees Celsius.
3. **Dry spell:** consecutive days with precipitation below 1 mm, ending on the selected day. The 1 mm boundary is an operational prototype convention, not a validated drought or ecological-impact threshold.

## Baseline and percentile

The fixed baseline is 2023-01-01 through 2024-12-31. Replay begins on 2025-01-01, so reference observations precede all assessed dates. No replay-period observations update the baseline.

For each metric and weather group, select baseline observations with circular calendar distance at most 30 days from the replay day's month and day. Month/day is mapped to a leap-year calendar of 366 days, making December–January and February 29 explicit. Most reference sets contain approximately 122 daily observations. Consecutive daily observations are dependent; the count is not an effective independent sample size.

For current value x and N valid reference values:

`percentile(x) = 100 × (number(reference < x) + 0.5 × number(reference = x)) / N`

Midrank tie handling is particularly relevant for zero rainfall and zero-length dry spells. An all-equal distribution gives the equal value a percentile of 50, not 100. Values outside the observed baseline range may reach 0 or 100; this does not imply a return period.

## Screening index and classes

`index = maximum of the available rainfall, heat and dry-spell percentiles`

Default classes:

- index ≥ 95: **Review first**;
- 85 ≤ index < 95: **Watch**;
- index < 85: **Routine**;
- no available metric: **No data**.

The thresholds are editable prototype choices. They are neither health thresholds nor validated alert boundaries. Because the index takes the maximum across three metrics, the proportion of flagged days can be substantially greater than 5% even with a 95 threshold. Two years of reference observations are insufficient for robust climatological return-period estimation.

If only some metrics are available, scoring uses those available metrics and the record is marked incomplete. Missingness can change ranks. The UI shows raw values, percentiles, reference counts and missingness. Display rounding is not used for classification.

Historical health-risk scores, nitrate indicators and urban context are displayed separately. None enters the weather index. `statusOfNitrate` units and category cutoffs have not been verified; the app deliberately assigns neither a concentration unit nor a safety category. Urban cover percentages follow their source field names; no causal effect is estimated.

## Field plan

Within the selected region and optional saved-site filter, sites with at least one valid screening metric are sorted by descending index. Ties are broken by alphanumeric site code with numeric ordering. When enabled, the plan greedily takes at most one site per exact weather group until the requested budget is filled or eligible groups are exhausted. Otherwise it takes the top sites regardless of group.

This is a transparent information-diversity heuristic. It is not travel-route optimization, a claim of optimal sampling design, or evidence that the selected sites are more polluted. Within a shared-weather group, this prototype has no validated basis to distinguish ecological risk between sites. A short plan is retained when there are too few eligible groups; redundant sites are not silently added.

## Mapping and accessibility

Overview country outlines are Natural Earth 1:110m public-domain data rendered offline using a Mercator projection. Overview bubbles are city markers, sized uniformly and labelled with site counts; their colour is the maximum site index in the city. The local view plots actual site coordinates on a grid without a street or river layer. Markers may overlap, so the searchable table remains the precise selection alternative. Geographic proximity is not treated as hydrological connectivity.

## Separate rainfall forecast experiment

Version 2 also includes an 18-feature logistic model for next-day recorded rainfall ≥10 mm. This is a separate task from the descriptive screening index. It uses a target-date temporal split, training-only standardization and seasonal baselines; details and actual test results are in `FORECAST_MODEL_CARD.md` and the pre-fit development protocol `FORECAST_PROTOCOL.md`. The experiment does not validate pollution, disease or field outcomes.

## Validation boundary

Core calculation tests cover ties, leap days, calendar gaps, dry-spell censoring, baseline isolation, ranking, group diversity and exports. Snapshot consistency is checked against source counts and daily values. Browser checks cover navigation, filters, replay, comparison, thresholds, exports and responsive layout. These checks establish implementation behaviour, not predictive validity, clinical utility or real-world environmental impact.

Next scientific steps would require verified weather provenance, richer and repeated water-quality labels, a prospectively defined outcome, geographically and temporally separated validation, threshold calibration with stakeholders, and a prospective human-supervised pilot.

## Version 3 investigation workflow

The multi-hazard protocol and findings are in `MULTIHAZARD_PROTOCOL.md` and `MULTIHAZARD_RESULTS.md`. They define eight weather targets, four comparators and a city-exclusion stress test. Mission control adds an explicit, optional urban-context planning weight and investigation checklists. None converts weather probability into a calibrated ecological-risk probability. Local field measurements are kept separately and do not alter model results.
