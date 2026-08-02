# Site

Static GitHub Pages-compatible site for the American Dream Reality Index.

## Files

- **`index.html`** — Latest ADRI value, trend vs. prior year, inline SVG line chart, per-domain grid, caveats, update-cadence notice. Uses `assets/app.js` and `assets/style.css`.
- **`methodology.html`** — Rendered from `docs/METHODOLOGY.md` by `scripts/render_site.py`. Do not edit by hand; regenerate.
- **`assets/style.css`** — All site styles. Deliberately plain (no framework, no CDN).
- **`assets/app.js`** — Vanilla JS that fetches `assets/adri_timeseries.json` and populates the DOM. Builds the line chart as inline SVG. No dependencies.
- **`assets/adri_timeseries.json`** — Written by `scripts/render_site.py`; copy of `data/index/adri_timeseries.json`.
- **`assets/adri_timeseries.csv`** — Convenience CSV for humans and spreadsheets.

## Regenerating

```bash
python3 scripts/run_all.py --skip-fetch  # produces index artifacts + rendered methodology
```

`render_site.py` on its own is fine when the underlying data has not changed:

```bash
python3 scripts/render_site.py
```

## GitHub Pages settings

When the repo is made public, enable Pages with:

- **Source**: Deploy from a branch
- **Branch**: `main`
- **Folder**: `/site`

Everything is relative-path, so no additional configuration is required. See `docs/update-cadence.md` § "License and public release" for the full checklist.
