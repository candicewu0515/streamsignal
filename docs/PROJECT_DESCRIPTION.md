# StreamSignal

**Track 6 — Resilience Informatics**

**Tagline:** From weather signals to focused water-ecosystem investigations.

## Problem

A weather forecast does not tell a monitoring team what happened in a stream. Teams need to connect an anticipated stressor to a field question, select sites under a limited visit budget, and record the observations needed to test that question. Repeated weather series across nearby sites and old health samples can otherwise give a misleading impression of current evidence.

## Eight calibrated tasks and network operations

StreamSignal calibrates rain, heat, low rainfall and hot-and-dry conditions over three and seven days. A five-city dashboard covers 21 weather groups. Each forecast is linked to reviewable sampling suggestions, One Health background and a local field notebook.

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

The comparison uses identical test windows and the original model's group-seasonal baseline. Brier skill measures probability-error reduction, not classification accuracy. Of 40 city-task results, 38 descriptive 90% intervals are above zero. Benevento 7-day low rainfall and Ghent 7-day hot-and-dry remain explicit exceptions. Local calibration requires past city labels, so these results do not demonstrate zero-data transfer to any European city. Deployment parameters and the scored held-out/local configurations are clearly distinguished.

The original Benevento past-weather rain result was −4.5%; its locally adapted professional-forecast follow-up was +54.1%. The research page retains the earlier benchmark and now adds all eight same-window comparisons and reliability plots.

Thresholds are selected on 2025 data. Rain has Watch/Review levels; heat, low rainfall and compound conditions have one Alert level. The red-rule revision occurred after old-rule 2026 results were viewed and is disclosed with preserved logs. Modeled references, shared weather, overlapping windows and live/archive differences limit retrospective interpretation.

Fresh alerts produce up to five distinct-group sampling suggestions. Historical impervious cover, sewage proximity and fecal context prioritise sites within each group. Rain visits are provisionally after the forecast wet period; heat/low-flow checks are provisionally within the window. Suggested measurements address turbidity, fecal indicators, dissolved oxygen, water temperature, flow and visual conditions. Dates and access require confirmation. Brief and calendar exports remain local.

See [current methods](NWP_EIGHT_TASKS.md) for definitions, exact thresholds, failures and reproducibility.

## Solution

StreamSignal provides a transparent workflow with a live-weather field workspace and an offline historical-research workspace: forecast a weather condition, inspect its ecological rationale, plan a field investigation and record measurements. A five-step English guided tour connects city alerts, One Health exposure context, mission planning, citizen observations and resilience planning. Detailed model evaluation, a professional field notebook and earlier analytical tools are grouped under Advanced.

The source snapshot has 106 sites across five European regions but only 21 exactly distinct daily weather series. The app makes this repetition visible and keeps historical health, nitrate and urban context separate from forecast outcomes.

## Original past-weather benchmarks

Eight tasks predict rain accumulation, heat exposure, low rainfall and hot-and-dry conditions over the next three and seven days. They compare regularized logistic regression and histogram gradient boosting with seasonal and persistence baselines. Models fit 2023–2024, select using 2025 probability error and report 2026 results. Target windows cannot cross split boundaries; missing input or outcome windows are excluded.

The simpler logistic model wins all eight validation comparisons. Three-day heat reduces Brier error by 28.6% versus seasonal history; seven-day rain improves by 20.1%; seven-day hot-and-dry improves by only 3.2%. The 39,648 exported task/group/issue-date predictions include overlapping windows and are not independent cases. Candidate comparisons, misses, false positives, calibration, uncertainty intervals and threshold tradeoffs remain inspectable.

The original three-day-rain stress test excludes each city from fitting, candidate selection and baseline construction. Benevento is worse than the other-city seasonal baseline (−4.5% skill), while the other cities have positive skill. This prompted the professional-forecast + local-calibration follow-up reported above.

## Alerts, One Health and resilience

In historical replay, five-city green/yellow/red cards show three- and seven-day probabilities with explicit trigger reasons. Each city value is the maximum among available weather groups, not an aggregate city event probability. A 2026 historical timeline exposes warning dates, verified weather dates, calendar-day leads, false alarms and misses. A community warning draft is generated locally and never sent.

The One Health view combines the latest source health sample available before issue with urban background. Pathogen, fecal and ARG scores remain dated historical context. Sewage proximity, impervious cover and historical fecal-score flags support a transparent investigation hypothesis, not a contamination prediction. Hospital proximity does not imply a discharge connection. Mechanism references explain runoff and conditional combined-sewer overflow without asserting that either occurred at a site.

The resilience matrix contrasts observed rain/heat frequency with an explicit, equal-weight urban-sensitivity index. Missing inputs remain unscored. A five-city comparison links adaptation discussions to OneAquaHealth's official Catalogue of Measures. This exploratory prioritization is not a validated damage model.

Citizen mode translates historical weather cues into plain-language, safe bank-side observation tasks. Users can save and export clarity, colour, flow, vegetation, wildlife, visible pressures and photo references. The export overlaps with concepts in the official public citizen-science guidance; the official import schema is unverified, so automatic integration is not claimed.

## From a prediction to field evidence

Mission control connects rain to observations of turbidity, conductivity, nutrients and runoff; heat to actual water temperature and dissolved oxygen; and low rainfall to actual water level, flow and habitat observations. General EPA/USGS mechanisms support the rationale. The exact checklists and planning rules are analyst-authored proposals, not validated site-specific prescriptions.

Analysts choose a probability threshold, visit budget, optional urban-cover priority weight and whether to avoid selecting sites with identical weather inputs. The priority formula is displayed and never changes the underlying model probability. Urban cover within a 500 m buffer is not a watershed or a measured runoff coefficient.

A downloadable investigation brief includes sites, coordinates, forecast windows, probabilities, planning preferences and measurement prompts. The Field notebook records water temperature, dissolved oxygen, pH, turbidity, conductivity, methods and notes. Corrections, reversible archiving and unit-labelled exports are supported. Empty values remain missing; local entries do not retrain models or become official source records.

## Live-to-field workflow and interoperability

The field workspace fetches group-centroid Open-Meteo forecasts using local calendar days, archives the inputs and parameters, and displays calibrated three- and seven-day probabilities. Both horizons drive the network board and suggested visits. Retrospective deployment scores and selected operating policies are visible, with explicit prospective-validation limits.

A UTC-timestamped field entry automatically links to an eligible earlier forecast. The prospective-evidence panel distinguishes real chronological pairs from demonstrations, legacy date-only entries and unpaired records. This provides a collection workflow, not completed prospective validation. Water measurements do not verify different weather variables.

Environmental measurements also export as FHIR R4 Location / Observation bundles. The generated structure passed the official R4 JSON schema; no Patient or clinical diagnosis is fabricated. Printable A4 forms include a site locator, coordinates, blank measurement cells and a local QR to the site's notebook. PWA support keeps the field workspace and records available without a connection after initial preparation.

## Additional measured planning result

Across 627 eligible historical days, a five-visit plan covering different exact weather groups represents 5.00 series, compared with 2.04 for the top-ranked sites. The mean descriptive screening index decreases from 95.30 to 93.83. This quantifies repeated-input reduction and its priority tradeoff, not improved pollution detection or field yield.

## Impact pathway and planned evaluation

The intended impact is more timely, useful water-ecosystem observations under a fixed visit budget. Weather probability triggers a specific investigation; the exported brief defines candidate measurements; the notebook preserves the resulting evidence. Researchers and responsible authorities, rather than the model, interpret water measurements and decide on any follow-up. No ecological or health improvement has yet been demonstrated. A proposed prospective comparison with routine monitoring would measure pre-specified verified water-quality changes per fixed number of completed visits, alongside missed changes, response times and workload. See `IMPACT_AND_PILOT.md` for the proposed design and current implementation gaps.

## Implementation and reproducibility

The browser uses HTML, CSS and JavaScript. A user-triggered Open-Meteo request retrieves weather without an API key; observations remain local. Historical research is deferred until requested. A service worker supports offline fieldwork, and mission/citizen interfaces have six language options. The optional local Python server provides inspectable exports. Separate Python/scikit-learn scripts reproduce the experiments and figures. Automated checks cover chronology, split boundaries, missingness, model selection, exported probabilities/metrics, planning rules, data-entry validation and local export behavior. Original source hashes and exact dependency versions are included.

## Limits and next step

All reported performance scores come from retrospective weather-label experiments; live forecasts are now available but not prospectively validated. No contamination, pathogen, dissolved-oxygen, water-temperature, river-flow or ecological-damage model is claimed. Weather provenance and publication latency are unverified, health labels are sparse, and no independent external or prospective field evaluation exists. Data-publication rights must be confirmed before a public demo.

The next step is a prospective pilot: verify source availability, define field procedures and costs with monitoring teams, collect repeated water measurements, and evaluate whether the forecast-guided workflow improves useful observations under a fixed budget.

## Sources and participant fields

- OneAquaHealth Resilience Map: https://apps.oneaquahealth.eu/resmap/
- Competition: https://oneaquahealth-ieee-hackathon.devpost.com/
- Mechanism references: EPA stormwater / dissolved oxygen and USGS dissolved oxygen, linked in the app.
- Natural Earth public-domain map outlines: https://www.naturalearthdata.com/

Independent prototype; no IEEE or OneAquaHealth endorsement is implied. Team details, eligibility, accurate assistance disclosure, public repository, permitted demo and 3–5 minute video still require participant completion. No competition entry has been submitted.
