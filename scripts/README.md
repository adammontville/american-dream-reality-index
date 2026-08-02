# Scripts

Retrieval, indicator processing, composite computation, and site rendering.

## Files

- **`config.py`** — Indicator definitions (name, domain, direction, source, fetch kind, anchor values with rationale). Domain weights. Path helpers. **This is where you go to change anything about the indicator set or its anchors** — but note that any change here is a MAJOR version bump per `docs/METHODOLOGY.md` §6.2.
- **`fetch_data.py`** — Refreshes raw sources from FRED, Census, and CDC Socrata when the relevant environment variable is set (`FRED_API_KEY`, `CENSUS_API_KEY`; CDC Socrata needs no key). Never crashes on network failure — logs a warning and leaves cached CSVs in place. Manual indicators are logged and left alone.
- **`process_indicators.py`** — Reads raw CSVs, applies no transformations, and writes one canonical JSON per indicator to `data/processed/`. This is a thin, deliberately boring step; normalization happens later.
- **`compute_index.py`** — Reads processed JSONs, applies fixed-anchor min-max normalization with directionality (per `METHODOLOGY.md` §5.1), aggregates within each domain (equal-weight per §5.4), applies fixed domain weights, and writes the composite time series to `data/index/adri_timeseries.json` (canonical) and `.csv` (convenience). Also produces per-indicator normalized scores and an equal-weight variant for §7.5 sensitivity.
- **`render_site.py`** — Copies `adri_timeseries.json` and `.csv` into `site/assets/` and renders `docs/METHODOLOGY.md` into `site/methodology.html` using a small built-in Markdown converter.
- **`run_all.py`** — Orchestrator. Runs the four steps above. Use `--skip-fetch` to run without touching the network.

## Design constraints in this directory

1. **Standard library only.** No `requests`, no `pandas`, no `numpy`. The pipeline is small enough that stdlib is the right choice; every dependency is a maintenance liability.
2. **No implicit web calls at import time.** Fetching is entirely inside `fetch_data.py`; every other script reads local files only.
3. **Never crash on network failure.** `fetch_data.py` returns 0 with warnings if it can refresh nothing, so `run_all.py` can still produce a valid index from cached raw files.
4. **Methodology is the source of truth.** If a rule in `METHODOLOGY.md` and a value in `config.py` disagree, the methodology wins and `config.py` is wrong. Bump the methodology version deliberately, not by drift.

## Documented deviations from METHODOLOGY.md

Both are flagged in code comments and documented in `docs/README.md`:

1. **VEP presidential-only carry-forward = 4 years** rather than the general §5.2 "at most one reference year." Necessary to keep the Civic domain populated between presidential elections given NOTES.md §6.3's presidential-only choice.
2. **Publication threshold**: a reference year is suppressed if fewer than 6 of 10 indicators are present or any domain has zero components. Tunable via `MIN_INDICATOR_COVERAGE` in `compute_index.py`.
