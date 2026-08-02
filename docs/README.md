# American Dream Reality Index

A small, transparent composite of U.S. structural conditions that shape how plausible the American Dream — durable prosperity plus intergenerational mobility — is in practice for the median resident.

The index tracks **enabling conditions**, not outcomes for any individual, and not a country's "greatness." It is deliberately slow-moving, backward-looking, and modest in scope: 10 indicators across six domains, updated once a year, published as static files on GitHub Pages.

## Status

- ✅ Methodology defined ([METHODOLOGY.md](METHODOLOGY.md))
- ✅ Indicator set frozen at 10 across six domains
- ✅ Source verification complete ([NOTES.md](NOTES.md))
- ✅ Repository skeleton in place
- ✅ Retrieval, processing, and composite scripts (Thread 2)
- ✅ Static site scaffold (Thread 2)
- ⏳ License selection and GitHub Pages enablement — deferred until public release
  ([update-cadence.md § License and public release](update-cadence.md#license-and-public-release))

## What the index measures

Six domains, ten indicators:

| Domain | Weight | Indicators |
|---|---|---|
| Education | 0.20 | NAEP grade-8 math + reading; Bachelor's attainment (25+) |
| Health | 0.20 | Life expectancy at birth; Drug overdose mortality |
| Prosperity | 0.20 | Real median household income; Supplemental Poverty rate; Prime-age employment-to-population ratio |
| Opportunity | 0.15 | Gini index of household income (mobility proxy) |
| Civic | 0.10 | Voter turnout of voting-eligible population (presidential-year) |
| Safety | 0.15 | Total incarceration rate per 100,000 |

See [METHODOLOGY.md §3](METHODOLOGY.md#3-indicator-set) for source URLs, direction, update frequency, and the reasoning behind each choice, and [§3.2](METHODOLOGY.md#32-indicators-considered-and-rejected) for what was considered and rejected.

## What the index does not measure

- Individual likelihood of success.
- National virtue, identity, or "greatness."
- State, county, or demographic-group conditions (the ADRI is national-only).
- Causes of change. It is a description, not an explanation.
- Real-time conditions. Data lag is 12–24 months.

## How to read a score

- **Scale**: 0–100. Higher is a more favorable structural condition for the Dream.
- **Anchors are fixed**: a 5-point change means the same thing in 2028 as in 2015. The index does not re-scale to recent history.
- **Weighting is a choice**: the site publishes both the design-weighted composite and an equal-weight variant so readers can see sensitivity to the weighting decision.
- **Every score is versioned**: each published index record pins the exact `METHODOLOGY.md` git tag it was computed under.

## Repository layout

```
american-dream-reality-index/
├── data/
│   ├── raw/
│   │   ├── manual/       # Vintage-of-record CSVs for indicators whose source
│   │   │                 # is a PDF, unstable XLSX, or cranky XML API. These
│   │   │                 # are the primary artifact updated by hand each cycle.
│   │   ├── api_cache/    # Automated-fetch cache CSVs (FRED, Census, CDC).
│   │   │                 # Bundled seed values live here so the pipeline runs
│   │   │                 # end-to-end without any API keys.
│   │   └── README.md
│   ├── processed/        # Per-indicator canonical JSONs written by
│   │                     # scripts/process_indicators.py. One file per
│   │                     # indicator, standard schema.
│   └── index/            # Composite outputs written by
│                         # scripts/compute_index.py:
│                         #   adri_timeseries.json  (canonical)
│                         #   adri_timeseries.csv   (convenience)
├── scripts/
│   ├── config.py             # Indicator definitions, anchors, weights.
│   ├── fetch_data.py         # Refresh raw sources when APIs are reachable.
│   ├── process_indicators.py # Raw CSV → processed JSON.
│   ├── compute_index.py      # Normalize + composite → adri_timeseries.*.
│   ├── render_site.py        # Copy artifacts + render METHODOLOGY.md → HTML.
│   └── run_all.py            # Orchestrator (default entry point).
├── docs/
│   ├── METHODOLOGY.md    # Full methodology — the primary document.
│   ├── NOTES.md          # Design notes, source verification, open questions.
│   ├── update-cadence.md # Update schedule, automation sketch, license notes.
│   └── README.md         # This file.
└── site/                 # Static site (GitHub Pages-ready).
    ├── index.html        # Latest ADRI + trend + line chart + per-domain grid.
    ├── methodology.html  # Rendered METHODOLOGY.md.
    └── assets/
        ├── style.css
        ├── app.js
        ├── adri_timeseries.json  # Copied from data/index by render_site.py.
        └── adri_timeseries.csv
```

## Pipeline: data → processed indicators → index → site

`scripts/run_all.py` is the single entry point:

```
python3 scripts/run_all.py             # full pipeline: fetch + process + compute + render
python3 scripts/run_all.py --skip-fetch  # skip network calls; use cached raw as-is
```

Individual steps for debugging:

```
python3 scripts/fetch_data.py          # refresh raw where credentials are set
python3 scripts/process_indicators.py  # data/raw/... → data/processed/*.json
python3 scripts/compute_index.py       # data/processed/*.json → data/index/adri_timeseries.*
python3 scripts/render_site.py         # copy artifacts + render methodology.html
```

**Credentials.** `fetch_data.py` reads two optional environment variables:

- `FRED_API_KEY` — St. Louis Fed FRED API (required to refresh indicators 5 and 7).
- `CENSUS_API_KEY` — U.S. Census Bureau API (recommended for indicators 2 and 8; small requests work without a key).

The CDC Socrata endpoint (indicator 3) needs no key. Indicators 1, 4, 6, 9, and 10 are `manual` — their `data/raw/manual/*.csv` files are the vintage of record and are updated by hand when the primary source releases (see `data/raw/manual/README.md`).

## Design principles

1. **Robustness over cleverness.** Long, stable, publicly-documented series only.
2. **Methodology before code.** No script is written before its rules are specified in `METHODOLOGY.md`.
3. **Epistemic humility.** Every score is versioned; every limitation is published alongside the number.
4. **Reproducibility.** Any snapshot can be recomputed from raw sources and the pinned methodology version.
5. **Static architecture.** GitHub Pages hosting; no backend.
6. **Small n.** 10 indicators, capped at 12.

## Relationship to other projects

- **BugOut Index** (`adammontville/bugoutindex`) is the operating precedent — a weekly societal-stability composite with an automated GitHub Pages pipeline. The ADRI is intentionally slower, smaller, and more design-first.
- A curated news/context layer, analogous to BugOut's "Current Signals," may be added later. It is deliberately deferred until the structural index itself is sound.

## Roadmap

- **Thread 1 — Design.** Methodology, indicator selection, feasibility assessment, repo scaffold. ✅
- **Thread 2 — Implementation.** Data retrieval, indicator processing, composite computation, static site. ✅
- **Later** — sensitivity analyses, back-computation of historical values under fixed anchors, optional curated context layer, license + public release.

## Deviations from the methodology, flagged for review

Thread 2 kept implementation aligned with `METHODOLOGY.md` and `NOTES.md` throughout, with two documented deviations that are explicit in code comments:

1. **Presidential-only VEP turnout with a 4-year carry-forward.** METHODOLOGY.md §5.2 sets a general "at most one reference year" carry-forward rule. Applied literally, a presidential-only VEP indicator disappears from every non-election year and the Civic domain collapses, forcing years 2010–2011, 2014–2015, 2018–2019, and 2022–2023 out of publication. NOTES.md §6.3 explicitly leans toward presidential-only turnout for v0.1 and calls this "revisit in Thread 2." The pipeline resolves the contradiction by carrying VEP forward across the full four-year presidential cycle, with every non-presidential year annotated in the ADRI record. Every biennial indicator (NAEP) is allowed at most one gap-plus-grace year, consistent with §5.2.
2. **Publication threshold.** The pipeline suppresses reference years where fewer than six of the ten indicators are present or where any domain has zero components. This is stricter than `METHODOLOGY.md` §5.3 says explicitly, but consistent with its spirit ("the most recent year for which every indicator has at least a provisional-or-better vintage"). The threshold is a constant (`MIN_INDICATOR_COVERAGE` in `scripts/compute_index.py`) so it can be tuned when Thread 3 or a v0.2 methodology bump revisits publication rules.

Both deviations are candidates for tightening once the methodology is next revised.

## Naming note

The working title "McAvoy Index" (referencing the *Newsroom* monologue that inspired the framing) remains under review. A public release will require a trademark check before any character-derived name is adopted. `american-dream-reality-index` is used here as a descriptive, non-branded working name.

## Contributing

Not currently open to external contributions. Once the site is public and the pipeline is stable, methodology issues and indicator suggestions will be tracked through GitHub Issues.

## License

TBD before public release. See [update-cadence.md § License and public release](update-cadence.md#license-and-public-release).
