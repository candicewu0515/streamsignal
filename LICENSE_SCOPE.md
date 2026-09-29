# License scope

The root [MIT License](LICENSE) covers the original StreamSignal application code and associated software documentation, including original JavaScript, HTML, CSS, tools and tests. It does **not** relicense third-party data, third-party software or other third-party assets.

## Excluded material

- **Research data and derived artifacts:** `data/` and `results/`, downloaded datasets, transformed snapshots, embedded data/parameter blocks (including those in `assets/nwp.js`), fitted coefficients, research outputs, and data reproduced in screenshots or reports are not granted an MIT data licence by this project. The original software logic in files containing embedded data remains MIT-licensed; the embedded material is excluded.
- **OneAquaHealth:** source observations, site metadata and urban/health context retain their original ownership and applicable terms. No redistribution licence has been verified. This MIT code licence does not supply permission to reuse that data.
- **Open-Meteo weather data:** retain [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and attribution requirements; see [Open-Meteo’s data licence](https://open-meteo.com/en/licence). StreamSignal aggregates weather into windows and computes derived probabilities; it does not relicense source weather as MIT.
- **Natural Earth boundaries:** retain their public-domain status; they are not placed under MIT by this project.
- **IBM Plex fonts:** retain the SIL Open Font License 1.1 in [assets/fonts/OFL.txt](assets/fonts/OFL.txt).
- **QR generator:** retains Kazuhiko Arase’s separate copyright and MIT licence in [vendor/qrcode-LICENSE](vendor/qrcode-LICENSE).

These exclusions define which material is covered by the project’s grant; they do not add conditions to the MIT licence for the original software. Existing permissions from third-party owners remain unaffected. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for provenance and attribution.
