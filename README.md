# American Dream Reality Index

A small, transparent composite of U.S. structural conditions that shape how plausible the American Dream — durable prosperity plus intergenerational mobility — is in practice for the median resident.

**Status: v0.1.0 — methodology, pipeline, and site scaffold complete. Not yet public; license and GitHub Pages settings deferred to public release (see [docs/update-cadence.md](docs/update-cadence.md#license-and-public-release)).**

## Quick start

```bash
python3 scripts/run_all.py --skip-fetch    # compute from bundled raw data
open site/index.html                       # inspect the static site locally
```

To refresh from live sources, set `FRED_API_KEY` and `CENSUS_API_KEY` and drop `--skip-fetch`. See [docs/README.md](docs/README.md#pipeline-data--processed-indicators--index--site) for the full pipeline description.

## Start here

- **[docs/METHODOLOGY.md](docs/METHODOLOGY.md)** — full methodology (purpose, indicators, normalization, weighting, composite formula, cadence, limitations).
- **[docs/README.md](docs/README.md)** — project overview, repo layout, and how to run the pipeline.
- **[docs/NOTES.md](docs/NOTES.md)** — design notes, source verification, indicators considered and rejected, open questions.
- **[docs/update-cadence.md](docs/update-cadence.md)** — update schedule, manual-refresh walkthrough, GitHub Actions sketch, license/public-release checklist.
