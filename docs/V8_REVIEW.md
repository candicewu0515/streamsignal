# Version 8 presentation review

- Removed the global Bulletin Numbers font face and every reference to it. Prose and headings use native Plex punctuation; tables use tabular numerals. Explicit probabilities, timestamps and coordinates use Plex Mono.
- The dashboard headline selects a current alert and shows its calibrated window, with a compact summary of the other cities. It does not claim an unmodeled event-onset day. Missing/stale forecasts do not create current alert headlines.
- The weather-group board fits all four hazards into its 926 px container at a 1024 px viewport. Table width is 926 px and collapsed desktop row height is 92.8 px, down from the reported 181 px. Dates, retrieval time and previous-fetch comparisons remain in expandable details. At 390 px, each group has four labelled hazard cells in a two-column layout; no page or board horizontal scroll is needed.
- Displayed group numbers are 1–21, including the board, map and live forecast. Stable stored group IDs remain 0–20; no data identifiers were changed.
- Mission control computes suggestions from eligible fresh forecasts on entry using the existing recommendation function. It does not accept a plan, write records or export anything automatically. Stale forecasts and filters remain respected. The long explanation has moved to Evidence.
- Clear city cards say “No alerts in 6/6 groups”, retaining available/current counts for incomplete coverage.

## Checks

85 JavaScript tests and 22 Python tests passed. Tests cover current versus stale headlines, clear city summaries, automatic suggestions without plan acceptance, existing numerical parity and all earlier checks. Models, source data and recommendation rules are unchanged.

At 390 × 844, dashboard, Mission control, live weather and research all have document width 390 px. Rendered text checks on all four pages found no contrast below 4.5:1. Keyboard navigation retained a 3 px ochre focus outline. Computed fonts are Plex Sans for body, Plex Sans Condensed for headings and Plex Mono for probability values; tables report tabular-nums.

The release is packaged as StreamSignal_v8_Eight_Task_Alerts.zip, replacing the v7 archive.

## Screenshots

[Desktop dashboard](screenshots/v8-dashboard.png) · [390 px dashboard](screenshots/v8-dashboard-390.png) · [390 px Mission control](screenshots/v8-mission-390.png).
