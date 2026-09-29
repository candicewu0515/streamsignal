# StreamSignal — eight calibrated weather tasks, version 8

**Professional forecasts → 3/7-day alerts → five-city dashboard → sampling suggestions → field evidence.**

**[Open the live demo](https://candicewu0515.github.io/streamsignal/)** · [Research evidence](https://candicewu0515.github.io/streamsignal/research.html)

Run `python3 tools/serve.py` here and open http://127.0.0.1:8765/. No API key or login is needed for the local non-commercial prototype. New UI and documentation are English; existing Mission/Citizen translations are drafts.

1. Open **Live dashboard**. Cached forecasts appear immediately; missing or stale network data refresh automatically. Use **Refresh all 21 groups** to update again. Compare hazard-specific city conclusions and select any of the 21 map dots to inspect a group. Filter city and 3/7-day horizon.
2. Open **Live weather** for exact event definitions, thresholds, dates and historical evidence. Rain has two levels; other hazards have a single Alert level.
3. Choose **Recommend up to 5 visits**. Fresh alerts yield distinct-group suggestions, site-context reasons and hazard-specific measurement prompts.
4. Review suggestions in Mission control, use them as the visit plan, or export a printable A4 brief and tentative calendar file. No messages or calendar writes occur.
5. Record actual field observations and inspect earlier forecast pairings. Local records and old archives are preserved; old-model forecasts must be refreshed to qualify for a new plan.

## Same-window comparison

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

These are retrospective Brier skill scores, not accuracy percentages. Cross-city results retain all 40 combinations, including Benevento 7-day low rainfall and Ghent 7-day hot-and-dry whose 90% intervals include zero. The research page shows eight reliability plots and exact bin counts. Deployment uses all-city pooled coefficients where applicable, while reported experiment scores use held-out pooled/local configurations.

Thresholds use 2025 data. The red rule was revised after earlier 2026 outcomes were viewed; both logs are retained. No future water quality or health outcome is predicted.

- [Current methods, limitations and reproducibility](docs/NWP_EIGHT_TASKS.md)
- [Project description](docs/PROJECT_DESCRIPTION.md) · [Demo script](docs/DEMO_SCRIPT.md)
- [Source parameters](results/nwp_multi/calibration_params_all_tasks.json) · [Complete results](results/nwp_multi/multi_summary.json)
- [Validation](docs/VALIDATION.md)

The offline field shell caches 24 resources, including four self-hosted IBM Plex WOFF2 fonts, after a successful localhost/HTTPS visit. Research data load separately; live refresh requires internet. First-load payload is measured in `results/loading_audit.json` (uncompressed bytes, not network timing).

Original OneAquaHealth data rights remain separate from Open-Meteo weather licensing. This local snapshot is not authorisation for public redistribution. The static demonstration is deployed to GitHub Pages. No competition submission has been made.

Dashboard labels are Red / Yellow / Alert / Clear; Clear means below weather triggers, not water safety. City summaries count groups at the stated severity and show their probability range. The optional rain change compares adjacent archived fetches of the same model and flags changed forecast dates. The map reuses the bundled country boundaries; grouped dots are separated into labelled city callouts for selection.

## River monitoring bulletin presentation

The interface uses petrol navigation, stone surfaces, explicit Red / Yellow / Alert / Clear labels and task-threshold probability bars. Headings and status lines replace promotional hero cards. IBM Plex fonts are self-hosted under the OFL and included in the offline cache. Models, source data and decision policies are unchanged. See [style verification and before/after screenshots](docs/BULLETIN_STYLE.md).

Version 8 fixes prose punctuation, derives the headline from fresh alerts, fits all four hazards in the group board, uses 1-based display group numbers and computes Mission control suggestions on opening. The underlying recommendation rules are unchanged and suggestions still require acceptance. See [v8 verification](docs/V8_REVIEW.md).
