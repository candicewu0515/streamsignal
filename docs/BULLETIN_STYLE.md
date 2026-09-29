# River monitoring bulletin

Presentation update, 29 September 2026. Forecast models, data, task definitions, thresholds, refresh rules and sampling logic are unchanged.

The application now uses petrol navigation, stone backgrounds, pale surfaces and the supplied slate text palette. Red, Yellow, Alert and Clear always have visible word labels. Corners are at most 4 px; shadows, gradients, spaced uppercase eyebrows and coloured card borders are removed. Factual headings and a plain status sentence replace promotional hero layouts. The bulletin timestamp is the actual latest saved retrieval time in UTC; no time is invented when no run exists.

IBM Plex Sans 400/500, Sans Condensed 500 and Mono are self-hosted WOFF2 files under the SIL OFL. Body and heading text use their native Plex fonts, including punctuation. Tables use tabular numerals. Mono is applied explicitly to probabilities, timestamps and coordinates. Font provenance and the licence are in THIRD_PARTY_NOTICES.md and assets/fonts/OFL.txt.

Probability bars receive the existing probability and decision policy without recalculation. Rain displays yellow and red threshold ticks. Heat, low rainfall and hot-and-dry each display one Alert tick. The numerical probability remains beside the bar, and its accessible name includes the probability, level and thresholds. Missing values never acquire a fabricated bar. Stale saved values retain their status.

General interpretation limits are consolidated on Evidence and linked from each page. Specific uncertainty intervals, weak results and methods disclosures remain with their research results.

## Verification

- 85 JavaScript tests and 22 Python tests passed.
- All 10 existing data files, fitted calibration assets and numerical modules matched their previous SHA-256 checksums. No model fitting was run.
- At 390 × 844, dashboard, live weather and research each have document width 390 px. Wide research tables scroll within their containers.
- Rendered HTML text contrast checks passed on the three pages: dashboard 412 elements at 390 px, live weather 104, Mission control 89 and research 96. Every checked text pair meets 4.5:1. Ochre labels use #8A6414 on #F4F5F2; white on the brighter ochre fill would fail, so it is not used. Map Clear labels use lichen on the pale surface, with light text inside lichen dots.
- Keyboard navigation showed a 3 px ochre focus outline in the navigation. Map links retain accessible group names and existing keyboard interaction.
- Eight live probability bars show ten total ticks: two per rain window and one for each other task/window.
- In the in-app browser on a fresh localhost origin, Offline & install reported **24 field resources cached; page controller active**. This includes all four font files. This verifies registration and cache population; a new disconnected Chrome session was not tested in this presentation pass.
- Browser comparisons reused saved forecasts. The appearance pass did not create field records, accept a sampling plan, export invitations or send messages.

## Screenshots

[Open the side-by-side gallery](BULLETIN_COMPARISON.html).

| Page | Before | After | 390 px |
|---|---|---|---|
| Dashboard | [PNG](screenshots/dashboard-before.png) | [PNG](screenshots/dashboard-after.png) | [PNG](screenshots/dashboard-390.png) |
| Live weather | [PNG](screenshots/live-weather-before.png) | [PNG](screenshots/live-weather-after.png) | [PNG](screenshots/live-weather-390.png) |
| Research | [PNG](screenshots/research-before.png) | [PNG](screenshots/research-after.png) | [PNG](screenshots/research-390.png) |

All before/after images are full-page captures at the same 1280 px browser viewport. Forecast values reflect the saved run visible during capture, not a new evaluation.

## Version 8 review

[Current review fixes and screenshots](V8_REVIEW.md). The before/after gallery above records the initial bulletin pass; v8 removes the global number-font substitution and further compacts the alert board.
