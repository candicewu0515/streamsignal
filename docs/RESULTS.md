# Retrospective planning results

## Question

For a fixed visit budget, how much repeated weather information does a site-ranking plan include, and what priority tradeoff results from restricting selection to one site per exact weather series?

## Design

Use the fixed 2023–2024 seasonal reference and replay all 629 calendar days from 2025-01-01 to 2026-09-21. The weather screen is the maximum available percentile of three-day rain, daily maximum temperature and consecutive dry days. The default threshold is 95. Each eligible day receives two plans: the top five sites and the top five sites with at most one representative per weather group. Ties use numeric-aware site-code order. The visit budget is an upper bound.

A third comparator is the exact expected number of groups in uniform random site sampling without replacement: sum over groups of `1 − C(N − group_size, budget) / C(N, budget)`. This is an analytic expectation, not a simulated field trial.

## Measured results

| Measure | Full replay result |
|---|---:|
| Eligible days | 627 / 629 |
| Valid weather-group days | 13,167 |
| Entirely missing group-days | 42 |
| Incomplete but scored group-days | 366 |
| Group-days at index ≥95 | 2,518 (19.12%) |
| Contiguous screening episodes | 820 |
| Top-five site's mean distinct groups | 2.0351 |
| Weather-diverse plan's mean distinct groups | 5.0000 |
| Uniform-random five-site expected groups | 4.3140 |
| Distinct-group ratio versus top-five sites | 2.457× |
| Top-five mean selected index | 95.3011 |
| Diverse-plan mean selected index | 93.8309 |
| Mean index reduction | 1.4702 points |
| Days with greater group coverage | 625 / 627 |

The coverage measure counts different input series, not independent samples. Other ecological evidence is deliberately excluded from the ranking.

## Historical extremes

- Largest observed three-day rain: 130.52 mm, 2025-11-14, Coimbra, weather group 8 (sites C7 and C19).
- Highest daily maximum temperature: 41.96 °C, 2025-08-11, Toulouse, weather group 18.
- Longest fully observed dry spell: 41 days, 2025-08-30, Coimbra, weather group 4. Its seasonal percentile is only about 90.16; a long raw spell need not exceed the 95 screen.

## Denominators and episode boundaries

Group-day rates count each exact series once per date. All-missing dates are excluded from observed denominators. Partial signal availability is flagged and still scored using available signals. Episode counts join consecutive above-threshold calendar dates within a group. A missing date splits an episode. Window and missing-data boundaries may censor episode duration; censoring is retained in exported data. Episodes are not independent natural disasters and can overlap across correlated groups.

The Results lab recomputes denominators, comparator values and episodes for the selected region, interval, threshold and budget. Default results above will change with those choices. A region with fewer than five groups uses fewer than five diverse visits; this is not hidden in the comparison.

## Interpretation

The experiment measures reduction of repeated weather inputs in a visit list. It does not measure pollution detection, sampling yield, health benefit, travel cost or optimal resource allocation. The priority reduction is the cost of the diversity rule under this descriptive index. There was no prospective field trial.

Machine-readable results: `results/analysis.json`, `daily_comparison.csv`, `weather_groups.csv`, `screening_episodes.csv`, `threshold_sensitivity.csv`, `monthly_screening.csv` and `regional_summary.csv`. Reproduce with `node tools/build_results.cjs`.
