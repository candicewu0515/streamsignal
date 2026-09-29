# Version 4 decision-support methods

This release adds transparent decision-support workflows to the frozen version 3 weather models. It does not refit models, add observed health outcomes, or issue live warnings.

## City alerts

For each city, hazard, issue date and horizon, take the maximum selected-model probability across distinct available weather groups. This is not the probability that any event occurs anywhere in the city. Site duplicates do not increase the maximum or group count. Display availability as available / total groups.

Default yellow ≥20%, red ≥40%; lower probabilities are green and missing forecasts are grey. Equality enters the higher level. These editable thresholds are demonstration choices, not optimized on the 2026 test outcomes or adopted from an official alert standard. Green means below trigger, not environmental safety.

The date menu is the intersection of available 3/7-day issue dates in 2026. Rain events are accumulated rain ≥20 mm over 3 days or ≥40 mm over 7 days. Heat is at least one maximum air temperature ≥30 °C. Low rainfall is total rain less than the horizon in mm. Hot-and-dry requires both heat and low rainfall. Low rainfall is not observed hydrological drought.

## Timeline and lead

One row is a weather group and forecast window. Positive/negative reference labels are frozen model-test labels. A red alert and positive label is a hit; red and negative is a false alarm; no red and positive is a miss; no red and negative is a correct rejection. Yellow is not counted as a red alert. All eligible issue dates from 2026-01-01 are retained, regardless of the selected city-card date. The snapshot ends 2026-09-21; this is not a complete calendar-year evaluation.

Verification day is the first cumulative rainfall-threshold crossing within that forecast window, or the first qualifying high-temperature day. Low-rainfall and compound events verify at window end. Lead = verification date minus completed issue date in calendar days, only for hits. It is not an operational latency measurement. Future weather is used only to evaluate the frozen prediction.

Repeated overlapping windows can describe the same weather episode. Counts and leads are therefore forecast-window diagnostics, not independent event counts. Gaps with missing predictors or outcomes are excluded, not interpreted as correct rejections. The stripe overview marks issue dates; the lead diagram and table show actual verification dates.

Demonstration: Coimbra group 7, issue 2026-02-02, 3-day rain probability 86.486%; target February 3–5, observed total 105.08 mm, 20 mm reached February 4: two calendar days of lead. This date was selected after inspecting results for presentation clarity. It is not a representative-skill claim.

## Historical One Health context

Use the most recent health sample dated on or before the selected issue date. No future sample is shown as prior evidence. Pathogen, fecal and ARG scores are source scaled scores, not probabilities of illness or contemporary contamination. Missing health records remain missing.

The exploratory background flags are: sewage distance midrank ≤25th percentile, impervious cover within 500 m ≥50%, and historical fecal-score midrank ≥75th percentile among sites with an eligible sample. Midrank = (number below + half the number tied) / number available. All three flags plus a red 3-day rain alert activate the combined priority hypothesis. No site in this snapshot meets all three default background flags; the interface does not invent a matching case or relax criteria to manufacture one. C2 illustrates two flags; its impervious cover is below 50%.

Urban sampling dates and source distance units are unverified. The app shows raw distance values without a unit claim and uses relative ranks for proximity. Distance to a hospital does not establish a wastewater discharge. Distance to a sewage station does not establish connectivity or combined sewer infrastructure.

Runoff and, where combined systems actually exist, wet-weather overflow motivate a sampling question. They do not establish a site-specific mechanism or contamination event. Trained teams must select appropriate laboratory methods and verify drainage connections.

## Resilience matrix

Exposure = 100 × observed days with daily precipitation ≥10 mm OR maximum air temperature ≥30 °C / days with both fields available, for 2025-01-01 through 2026-09-21. Count the union once. Sites sharing a weather group share exposure; they are not independent observations.

Sensitivity = equal-weight mean of impervious percentage, 100 − vegetation percentage (both within 500 m), and 100 × (1 − sewage-distance midrank). All three inputs must be valid and present; otherwise sensitivity is unscored. These source percentages are used as stored. The app does not estimate an intervention's ecological effect.

Quadrants split at the medians among fully scored sites; ties count as above-or-equal. Cohort composition affects these relative priorities. The matrix is exploratory, not a validated vulnerability or health-risk index. Its historical period is independent of the Alerts issue-date selection.

City rain/heat frequencies pool distinct weather-group days once per group, without multiplying by site count. Comparing their frequencies depends on the chosen hazard definitions; frequency is not severity or expected harm. Adaptation text proposes locally reviewed restoration options, not site-specific engineering advice.

## Citizen data and interoperability

The task uses historical weather and carries that label into the export. Suggested bank-side observations happen only when weather has passed, paths are open and access is safe. Approximate 24-hour timing is a task template, not an ecological measurement protocol or safety guarantee.

The notebook records user-entered site, date, demonstration/actual status, clarity, colour, flow, odour, vegetation, wildlife, litter, erosion, photo references and notes. “Not observed” stays explicit. No photograph is uploaded, embedded or analysed; no location is tracked. Records are separate from source data and do not update models. Export provides durable copies; browser storage is local and may be cleared by the browser.

Official public guidance supports concept alignment. No official import schema or API has been verified. The CSV mapping notes distinguish overlapping concepts from supplementary local metadata. Manual transfer and official app registration remain separate actions. No message, record or warning is sent to a third party by this prototype.

## Primary references

- [OneAquaHealth citizen-science project and app guidance](https://www.oneaquahealth.eu/citizen-science-project/)
- [Official Citizen Science App](https://app.enora-oah.eu/)
- [OneAquaHealth Catalogue of Measures](https://www.oneaquahealth.eu/2026/05/12/oneaquahealth-catalogue-of-measures/)
- [EPA combined sewer overflow basics](https://www.epa.gov/npdes/combined-sewer-overflow-basics)
- [EPA stormwater mechanisms](https://www.epa.gov/nutrientpollution/sources-and-solutions-stormwater)

These sources support observation concepts and general mechanisms, not the model's accuracy or this prototype's numerical thresholds.
