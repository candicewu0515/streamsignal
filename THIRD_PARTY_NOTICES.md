# Third-party sources

## OneAquaHealth research snapshot

Source application: https://apps.oneaquahealth.eu/resmap/

Source data service used by that application: https://api.enora-oah.eu/api

Downloaded 2026-09-28 America/Chicago. Weather, site, health-risk, nitrate and urban-context data retain their source values. `data/snapshot.js` is a compact transformed copy for this hackathon prototype, and `data/audit.json` records source hashes. No redistribution licence has been verified. Public access must not be treated as a grant of redistribution rights. This repository retains source attribution and does not grant a new licence to third-party data.

This project is independent and does not imply OneAquaHealth or IEEE endorsement. No OneAquaHealth logo is reproduced.

## Natural Earth

Country boundaries: Natural Earth 1:110m Admin 0 Countries.

- https://www.naturalearthdata.com/
- https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson

Natural Earth describes its map data as public domain. The app retains geometry for Europe and neighbouring continents and removes unnecessary attributes. Country boundaries are a visual orientation aid, not authoritative surveying or political guidance.

## Application implementation

The original application code uses browser APIs and browser/Node standard APIs, with no bundled third-party JavaScript frameworks. The icon is an original SVG. No model API, authentication token, password or private key is present in the app. Original StreamSignal code is licensed under the root MIT LICENSE. This does not grant rights in source data or relicense third-party assets; see LICENSE_SCOPE.md.

## Optional model reproduction

The offline interface has no external JavaScript dependencies. The separate Python training tool uses NumPy, SciPy, scikit-learn and matplotlib, plus their dependencies. Exact installed versions are recorded in `tools/requirements-model.txt`. Python environments and third-party package binaries are not bundled. See each package’s official distribution for its licence. The fitted coefficients and generated figures are included for inspection.

## IBM Plex fonts

IBM Plex Sans Regular and Medium, IBM Plex Sans Condensed Medium, and IBM Plex Mono Regular are bundled as complete WOFF2 fonts from [IBM’s official Plex repository](https://github.com/IBM/plex), downloaded 29 September 2026. Source paths: `packages/plex-sans/fonts/complete/woff2/`, `packages/plex-sans-condensed/fonts/complete/woff2/`, and `packages/plex-mono/fonts/complete/woff2/`.

Copyright IBM Corp. Licensed under the SIL Open Font License 1.1. The unmodified licence is bundled at `assets/fonts/OFL.txt`; font binaries are covered by `SHA256.json`. The fonts are self-hosted and require no external font service.

## Open-Meteo weather data

Weather data by [Open-Meteo](https://open-meteo.com/) are provided under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), as described in [the provider’s licence](https://open-meteo.com/en/licence). StreamSignal aggregates daily forecasts and fits calibration models; its derived probabilities are not the provider’s unmodified output. The project’s MIT code licence does not replace the data licence.
