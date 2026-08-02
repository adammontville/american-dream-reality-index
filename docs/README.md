# American Dream Reality Index

A small, transparent composite of U.S. structural conditions that shape how plausible the American Dream — durable prosperity plus intergenerational mobility — is in practice for the median resident.

The index tracks **enabling conditions**, not outcomes for any individual, and not a country's "greatness." It is deliberately slow-moving, backward-looking, and modest in scope: 10 indicators across six domains, updated once a year, published as static files on GitHub Pages.

## Status

This repository is currently in **design phase (Thread 1)**. It contains methodology and documentation only. There is no retrieval code, no computed index values, and no site yet.

- ✅ Methodology defined ([docs/METHODOLOGY.md](METHODOLOGY.md))
- ✅ Indicator set frozen at 10 across six domains
- ✅ Source verification complete ([docs/NOTES.md](NOTES.md))
- ✅ Repository skeleton in place
- ⏳ Retrieval, computation, and site code — **Thread 2**

## What the index measures

Six domains, ten indicators:

| Domain | Weight | Indicators |
|---|---|---|
| Education | 0.20 | NAEP grade-8 math + reading; Bachelor's attainment (25+) |
| Health | 0.20 | Life expectancy at birth; Drug overdose mortality |
| Prosperity | 0.20 | Real median household income; Supplemental Poverty rate; Prime-age employment-to-population ratio |
| Opportunity | 0.15 | Gini index of household income (mobility proxy) |
| Civic | 0.10 | Voter turnout of voting-eligible population |
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
│   ├── raw/           # Source files as downloaded (populated in Thread 2)
│   ├── processed/     # Cleaned, normalized indicator series (Thread 2)
│   └── index/         # Composite index time series, e.g. adri_timeseries.json (Thread 2)
├── scripts/           # Retrieval and computation scripts (Thread 2)
├── docs/
│   ├── METHODOLOGY.md # Full methodology — the primary document in this repo
│   ├── NOTES.md       # Design notes, source verification, indicators considered
│   └── README.md      # This file
└── site/              # GitHub Pages static site (Thread 2)
```

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

- **Thread 1 (this thread) — Design.** Methodology, indicator selection, feasibility assessment, repo scaffold.
- **Thread 2 — Implementation.** Data retrieval, indicator processing, composite computation, static site.
- **Later** — sensitivity analyses, back-computation of historical values under fixed anchors, optional curated context layer.

## Naming note

The working title "McAvoy Index" (referencing the *Newsroom* monologue that inspired the framing) remains under review. A public release will require a trademark check before any character-derived name is adopted. `american-dream-reality-index` is used here as a descriptive, non-branded working name.

## Contributing

Not currently open to external contributions. Once Thread 2 stabilizes and a public site exists, methodology issues and indicator suggestions will be tracked through GitHub Issues.

## License

TBD before public release.
