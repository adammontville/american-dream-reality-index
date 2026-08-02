[![AGPL License](https://img.shields.io/badge/license-AGPL%20v3-blue)](./LICENSE.md)
[![Commercial License](https://img.shields.io/badge/license-Commercial-orange)](./COMMERCIAL_LICENSE.md)

# American Dream Reality Index

A small, transparent composite of U.S. structural conditions that shape how plausible the American Dream — durable prosperity plus intergenerational mobility — is in practice for the median resident.

**Status: v0.1.0 — methodology, pipeline, and site scaffold complete. GitHub Pages enablement and public visibility pending; see [docs/update-cadence.md](docs/update-cadence.md#5-license-and-public-release).**

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

## License

The American Dream Reality Index is available under a dual-license model:

1. **GNU Affero General Public License v3.0 (AGPL-3.0)**
   - Applies to open-source use.
   - You are free to use, modify, and distribute the software under the terms of the AGPL-3.0.
   - Any hosted derivative that interacts with users over a network must publish its source under the same terms.
   - Full license text: [LICENSE.md](./LICENSE.md).

2. **Commercial License**
   - Required for proprietary or commercial use cases such as integrating ADRI into closed-source systems, paid SaaS platforms, or free websites supported by advertising or membership of any kind.
   - See [COMMERCIAL_LICENSE.md](./COMMERCIAL_LICENSE.md) or contact adam.w.montville@gmail.com to inquire.

By contributing to this project, you agree to license your contributions under both the AGPL-3.0 and the commercial license.
