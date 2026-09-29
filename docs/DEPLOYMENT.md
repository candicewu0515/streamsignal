# GitHub Pages deployment

Live app: https://candicewu0515.github.io/streamsignal/
Repository: https://github.com/candicewu0515/streamsignal

GitHub Pages serves the main branch root with .nojekyll. All application URLs, PWA scope and service-worker resources are relative to the project path. The website has no backend and requires no login. Open-Meteo requests run directly from the browser. Field notes and forecast archives remain in browser-local storage; file exports use browser downloads on the public host.

The repository contains the application, runtime research assets, model parameters, evidence, tests and third-party attribution. Raw download caches, local exported files, environment files and local observations are excluded. Publication does not change third-party ownership or data licence terms.

Before pushing app changes, run node --test tests/*.test.cjs and python3 tools/build_field_release.py. Keep sw.js and results/loading_audit.json in the same commit so browsers receive a new cache version. Push to main to rebuild Pages. Check the Pages deployment status and verify dashboard, research and offline cache on HTTPS.
