# Multi-hazard findings — version 3

Eight weather tasks extend the original next-day rainfall demonstration to three- and seven-day investigation windows. These models predict weather labels, not measured ecological response. All future target dates remain within their train/validation/test split. The original snapshot was already explored in development; this is not an independent external test.

## Measured temporal results

Positive Brier skill means lower probability error than the same-group seasonal baseline. Candidate selection used validation-year 2025 only. Both linear and boosted candidates were retained in the comparison; logistic regression won every validation comparison. Complexity was not used as a substitute for performance.

| Target | Horizon | Test rows | Events | Selected Brier | Seasonal Brier | Skill | AUC | Precision | Recall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Rain accumulation | 3d | 5082 | 551 | 0.0814 | 0.0980 | 17.0% | 0.768 | 31.0% | 53.4% |
| Heat exposure | 3d | 5082 | 862 | 0.0591 | 0.0828 | 28.6% | 0.962 | 73.5% | 74.0% |
| Low rainfall | 3d | 5082 | 2779 | 0.2170 | 0.2575 | 15.7% | 0.711 | 65.1% | 79.8% |
| Hot and dry | 3d | 5082 | 736 | 0.0685 | 0.0852 | 19.6% | 0.945 | 61.4% | 74.9% |
| Rain accumulation | 7d | 4830 | 490 | 0.0763 | 0.0955 | 20.1% | 0.762 | 22.6% | 67.1% |
| Heat exposure | 7d | 4830 | 1074 | 0.0717 | 0.0931 | 23.0% | 0.955 | 72.1% | 84.8% |
| Low rainfall | 7d | 4830 | 2080 | 0.2220 | 0.2578 | 13.9% | 0.692 | 50.0% | 86.0% |
| Hot and dry | 7d | 4830 | 788 | 0.0926 | 0.0956 | 3.2% | 0.906 | 54.4% | 81.3% |

There are 39,648 exported task/group/issue-date predictions. This count includes overlapping windows and repeated use across tasks; it is not a count of independent observations. Low-rain and hot-and-dry targets can have very different prevalence across cities and seasons. All eight tasks are displayed to avoid selecting only the strongest headline. Seven-day compound skill is modest.

## Geographic stress test

For three-day rain, each city is excluded entirely from fitting, candidate selection and baseline construction. Models fit other cities' 2023–2024 observations, select on those cities' 2025 observations, and test on the held-out city in 2026. The baseline pools other-city training labels within ±30 calendar days. It differs from the same-group temporal baseline.

| Excluded city | Selected model | Model Brier | Pooled seasonal Brier | Skill |
|---|---|---:|---:|---:|
| Benevento | logistic | 0.1089 | 0.1042 | -4.5% |
| Coimbra | logistic | 0.1133 | 0.1443 | 21.4% |
| Ghent | logistic | 0.0462 | 0.0495 | 6.6% |
| Oslo | logistic | 0.0877 | 0.0892 | 1.7% |
| Toulouse | logistic | 0.0822 | 0.0861 | 4.5% |

Benevento underperforms the pooled seasonal baseline. This is direct evidence that same-region temporal gains do not guarantee transfer. No deployment-quality transfer claim is made.

## From probability to a field question

Mission control maps a selected weather task to a specific question and measurement checklist. Rain prompts review of turbidity, conductivity, nutrients and local runoff observations; heat prompts water-temperature and dissolved-oxygen observations; low rainfall prompts checks of actual water level, flow and habitat connectivity. The compound task combines weather conditions, not unobserved water outcomes.

These are analyst-authored investigation suggestions supported by general mechanisms in [EPA stormwater guidance](https://www.epa.gov/nutrientpollution/sources-and-solutions-stormwater), [USGS dissolved oxygen information](https://www.usgs.gov/water-science-school/science/dissolved-oxygen-and-water) and [EPA dissolved oxygen mechanisms](https://www.epa.gov/caddis/dissolved-oxygen). The references support the rationale, not the exact forecast thresholds, visit timing, priority weights or site-specific protocols. The field team must define appropriate procedures and current access conditions.

## Explicit planning preferences

The default priority is the model probability. An optional urban-cover uplift changes the priority index but never changes the model probability. Urban cover within 500 m is local context, not catchment imperviousness or measured runoff; its historical availability is unverified. Missing context is labelled and receives no uplift. Budgets and one-per-weather-group selection are explicit and exportable. No route, travel time, ecological benefit or optimal sampling design is estimated.

## Observation register

The Field notebook captures site, date, water temperature, dissolved oxygen, pH, turbidity, conductivity, method and notes. Empty fields remain missing. At least one numeric measurement and a method are required. Broad input bounds are entry checks, not ecological safety limits. Corrections and reversible archiving are supported. Records remain in the browser until exported; local records do not retrain any model or alter the official snapshot.

## Reproduction and limitations

Run `python tools/train_multihazard.py`, then `python tools/report_multihazard.py` in the supplied dependency environment. Full protocol: `MULTIHAZARD_PROTOCOL.md`. Full probabilities and comparisons are in `results/multihazard_predictions.csv` and `results/multihazard_comparison.csv`. Bootstrap intervals, calibration bins, thresholds and monthly performance are in `results/multihazard_metrics.json`.

Seven-day input windows and complete future labels exclude missing periods and may bias the evaluated sample toward complete observations. Daily source publication latency and upstream weather provenance remain unverified. No numerical weather prediction benchmark, independent external dataset, prospective pilot or measured water-quality endpoint has been evaluated. These limits are part of the product, not hidden in a claim of environmental early-warning accuracy.
