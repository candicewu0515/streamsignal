# Eight-task forecast calibration — current v7 release

Four weather conditions are evaluated over three and seven local calendar days, starting tomorrow: heavy rain (total ≥20/40 mm), heat (maximum air ≥30 °C), low rainfall (total <3/7 mm), and hot-and-dry (both heat and low rainfall). Low rainfall is a short weather condition, not a diagnosis of hydrological drought.

## Matched-window evidence

| Task | Original Brier skill | Forecast + calibration | Matched windows |
|---|---:|---:|---:|
| Heavy rain, 3 days | 17.0% | 56.2% | 5082 |
| Heat, 3 days | 28.6% | 79.2% | 5082 |
| Low rainfall, 3 days | 15.7% | 58.7% | 5082 |
| Hot and dry, 3 days | 19.6% | 65.0% | 5082 |
| Heavy rain, 7 days | 20.1% | 52.1% | 4830 |
| Heat, 7 days | 23.0% | 75.5% | 4830 |
| Low rainfall, 7 days | 13.9% | 46.8% | 4830 |
| Hot and dry, 7 days | 3.2% | 40.8% | 4830 |

Brier skill is relative probability-error reduction versus the seasonal baseline, not percent accuracy. Both models are scored on identical matched group/date rows with the original same-group seasonal baseline. They have different information inputs and fitting periods; this is not an algorithm-only ablation.

## Fitting and transfer

The supplied experiment fits 2024, selects A/B/C/D on mean 2025 city Brier skill (worst city breaks ties), refits 2024–2025, and scores through 21 September 2026. The pooled part excludes the tested city; local adaptation uses that city's historical labels. B is entirely local. A new city without historical calibration cannot inherit these city-specific performance claims.

Deployment uses the `deployment` block in `results/nwp_multi/calibration_params_all_tasks.json`; pooled components use all five cities. Reported metrics, reliability bins and threshold outcomes use the `heldout` configuration, not a separately scored deployment fit. The browser archives the exact parameters, features, thresholds, version, source hash, dates, coordinates and retrieval time.

Inputs: rain/dry = [log1p(total mm), log1p(max daily mm)]; heat = [max C, max C²/100]; compound = [max C, max C²/100, log1p(total mm)]. A/B use intercept + coefficient dot product; D applies local intercept and slope to the pooled coefficient score. Missing values remain unavailable. Existing archived forecasts keep their old version and cannot qualify for current sampling suggestions.

## All 40 city-task results retained

38 descriptive 90% interval lower bounds exceed zero. Benevento dry_7: +15.3%, interval [−0.35%, 33.44%]; Ghent compound_7: −0.22%, [−43.46%, 25.78%]. Benevento's reference event prevalence exceeds its average predicted probability; this is consistent with a distribution shift but does not establish its cause. Ghent has only 67 positive overlapping group-windows, not 67 independent events. Both exceptions remain visible in the UI.

Intervals use 500 resamples of blocks of seven ordered available issue dates, grouping rows for a date together within each city. They are descriptive, unadjusted for multiple comparisons, and do not account for the entire model-selection process. Shared weather and overlapping windows reduce independence.

## Operating levels and threshold revision

**Operational choice:** use the supplied rain_3 two-level policy (Watch ≥0.21; Review ≥0.57), replacing v6’s coincident 0.25/0.25 levels. This gives a distinct broad screening cue and a higher-confidence review cue, consistent with the eight-task experiment. It is a workflow choice, not a claim that this policy statistically outperforms v6: v6 selected thresholds using city-day any-group alerts with a false-day cap, while this experiment uses group-window recall and precision without that cap. Their workload statistics are not directly interchangeable. The 2026 outcomes below describe the chosen rule; they were not used here to tune thresholds.

Yellow = highest grid threshold with 2025 recall ≥80%. Red = lowest strictly higher grid threshold with 2025 precision ≥80%, or disabled if unavailable. Grid: 0.02 to 0.98 in steps of 0.01. These are validation targets, not promises for test/live performance. No false-alert budget is imposed by this experiment.

Rain shows Watch/Review using both thresholds. Heat, low rainfall and hot-and-dry show one Alert level at yellow; their research red thresholds remain archived. The separation is not always 0.01: dry_7 is 0.37/0.41 and compound_7 is 0.45/0.47. Single-level display is a usability policy, not a new statistically fitted threshold.

The first red rule (precision ≥50%) collapsed onto yellow for all eight tasks. It was replaced using 2025 data after the original-rule 2026 results had already been viewed. `multi_output_threshold_rule1.txt` is preserved. Previous 2026 model-development results had also been inspected. This is not a pristine external test.

Three-day rain test: watch recall 81.9%, precision 58.7%, 1.68 false alerts per group-month; red recall 46.6%, precision 88.0%, 0.19 false alerts per group-month. The workload denominator is 21 groups × nine represented calendar months, including partial September. Counts concern overlapping daily windows; they are not event counts or a rate normalized to 30 fully observed days.

## One Health actions

On first dashboard opening, saved forecasts appear immediately and incomplete or stale coverage refreshes automatically; fresh complete coverage is reused. Manual refresh remains available. The dashboard refreshes 21 groups with three concurrent requests and explicit current, stale, missing and failed states. City cards count flagged groups; they do not display calibrated city-level probabilities. All four hazards and the chosen horizon feed suggestions for up to five distinct groups. Within a group, imperviousness, relative sewage proximity and dated fecal context prioritise sites; this is historical context plus mechanism-based investigation, not predicted contamination.

Rain: provisional 24–48-hour calendar-day visit after the last wet forecast day, with event-ending confirmation. Heat/compound: provisional peak-air-temperature day. Low rainfall: final day of the forecast window. Heat and low-flow checks include water temperature, dissolved oxygen, flow/pool connectivity and visual observations. These are reviewable research suggestions, not optimal visit-time estimates. Safe access and timing must be checked. One-page brief and tentative ICS exports create local files only.

## Reproducibility and scope

The source parameters, full summary, current and original-rule logs are retained in `results/nwp_multi/`. Integration refitted all 40 deployment profiles and verified equality with supplied parameters, checked consecutive forecast windows, and exported independent sklearn probability fixtures for browser parity tests. See `integration_audit.json` and `tests/nwp-multi-parity.json`.

`tools/nwp/evaluate_multi.py` preserves the experiment with portable path configuration: set STREAMSIGNAL_NWP_CACHE to the directory containing g0.json..g20.json and g0_L47.json..g20_L47.json; optionally set STREAMSIGNAL_NWP_OUTPUT to a separate verification directory. It requires the included training tools/snapshot/original prediction CSV and the project Python dependencies. Running the full experiment is separate from building the app; `tools/build_nwp_bundle.py` rebuilds the installed offline parameter and research bundles, and `tools/build_field_release.py` regenerates the service-worker version.

Modeled/reanalysis reference data are not rain-gauge observations. Archived day-specific leads are not a single issued live run; provider changes and local/UTC day definitions can affect transfer. No prospective weather, water-quality, health or impact validation is claimed. Superseded v6 generated outputs and documents were removed during release cleanup. Current eight-task source results, both threshold-rule logs and original-model comparison inputs are retained.
