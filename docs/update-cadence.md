# Update cadence, automation, and public-release checklist

This is the operations companion to [METHODOLOGY.md](METHODOLOGY.md). It says
*when* to run the pipeline, *how* to automate it, and what to do before
making the repo public.

---

## 1. Indicator update frequencies

| Indicator | Cadence | Typical publication window | Retrieval kind |
|---|---|---|---|
| 1. NAEP grade-8 math + reading | Biennial (even years) | Following Jan–Feb | manual (CSV updated by hand) |
| 2. Bachelor's attainment (ACS S1501) | Annual | ~September | API (Census) |
| 3. Life expectancy at birth | Annual (final) | 12–18 months after year end | API (CDC Socrata) |
| 4. Overdose mortality (age-adjusted) | Annual (final); monthly provisional | Final ~14 months after year end | manual (NCHS Data Brief) |
| 5. Real median household income | Annual | ~September (of year *t*+1) | API (FRED) |
| 6. Supplemental Poverty Measure | Annual | ~September (Report P60) | manual (XLSX layout not schema-stable) |
| 7. Prime-age (25–54) EPOP | Monthly (annualized) | Complete year *t* available in Jan of *t*+1 | API (FRED) |
| 8. Gini index (ACS B19083) | Annual | ~September | API (Census) |
| 9. VEP turnout (presidential) | Every 4 years | Nov after election; certified by ~Dec/Jan | manual (Election Lab CSV/XLSX) |
| 10. Total incarceration rate | Annual | Prison late in year *t*+1; Jail midyear of *t*+1 (preliminary) | manual (BJS PDF-primary) |

**Anchor year for the composite.** Because indicator #6 (SPM) and indicator #3 (life expectancy final) both land 12–18 months after the reference year, the composite for calendar year *t* is publishable no earlier than **Q4 of *t*+1**, and often into *t*+2 if BJS incarceration figures are late.

## 2. Realistic update schedule

**Full annual refresh — Q4 of year *t*+1 (recommended January of year *t*+2 if any source is late):**

```
python3 scripts/run_all.py
git add data/ site/assets/adri_timeseries.*
git commit -m "adri: refresh reference year <t>"
git push
```

This is the only run that publishes a new headline ADRI reading.

**Interim refreshes** — permitted only when:

- A primary source revises a prior year's value (e.g., Census re-releases an ACS estimate, BJS restates prisoner counts).
- A biennial indicator publishes its next vintage (NAEP even years; VEP presidential years).

Interim refreshes bump the PATCH version per METHODOLOGY.md §6.2 and do **not** produce a new headline year unless one is genuinely ready.

**No sub-annual composite.** The ADRI is not published quarterly. Component-level charts on the site (e.g., prime-age EPOP annual points) may show intra-year variation over time; the composite itself remains annual.

## 3. Manual data update walkthrough

For each of the five manual indicators, updating the CSV under `data/raw/manual/`:

1. Download the fresh source file:
   - **NAEP (1)**: NCES / NAGB main assessment release page.
   - **Overdose (4)**: NCHS Data Brief for the reference year (e.g., DB 549 for 2024).
   - **SPM (6)**: Census P60 Income and Poverty in the United States report; SPM section.
   - **VEP (9)**: UF Election Lab turnout data downloads.
   - **Incarceration (10)**: BJS Prisoners + Jails statistical tables (PDF); NACJD microdata as fallback.
2. Compute the value per the CSV comment header (e.g., NAEP = arithmetic mean of grade-8 math and grade-8 reading national-public scale scores).
3. Append or update the row in `data/raw/manual/<indicator_id>.csv`.
4. Update the `# vintage:` line at the top of the CSV to the new pull date.
5. Optional but recommended: archive the source PDF/XLSX under `data/raw/manual/archive/<indicator_id>/<vintage>.<ext>` locally (not committed; the CSV plus its provenance header is the reproducibility contract).
6. Run `python3 scripts/run_all.py --skip-fetch` and inspect the diff in `data/index/adri_timeseries.json`.
7. Commit with a message like `adri: refresh overdose 2025 (NCHS DB xxx)`.

## 4. Light automation sketch (GitHub Actions)

The repo does not currently ship a workflow file. Below is a working sketch that Thread 3 (or a follow-on) can drop under `.github/workflows/refresh.yml` when the schedule is worth automating.

```yaml
# .github/workflows/refresh.yml — SKETCH, not enabled yet
name: ADRI quarterly refresh

on:
  schedule:
    # Second Tuesday of Jan, Apr, Jul, Oct at 15:00 UTC.
    # Cron's day-of-week vs day-of-month interaction is quirky; a simple
    # first-Tuesday approximation is `0 15 1-7 1,4,7,10 2`.
    - cron: "0 15 1-7 1,4,7,10 2"
  workflow_dispatch: {}

jobs:
  refresh:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Run pipeline
        env:
          FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
          CENSUS_API_KEY: ${{ secrets.CENSUS_API_KEY }}
        run: |
          python3 scripts/run_all.py

      - name: Commit refreshed artifacts if anything changed
        run: |
          git config user.name  "adri-bot"
          git config user.email "adri-bot@users.noreply.github.com"
          git add data/ site/assets/adri_timeseries.*
          if git diff --cached --quiet; then
            echo "No changes to commit."
          else
            git commit -m "adri: automated refresh $(date -u +%Y-%m-%d)"
            git push
          fi
```

Notes:

- **Quarterly, not weekly.** The ADRI is a slow index; running less often reduces API-quota pressure and avoids meaningless intermediate commits.
- **Manual indicators.** The workflow will *not* touch the five manual CSVs. It only refreshes API-backed indicators and recomputes. Every manual update is still done by a human.
- **Failure handling.** `scripts/fetch_data.py` is designed to log warnings but not crash on missing credentials or network failure. The workflow will simply commit no changes on a bad-network day.

## 5. License and public release

The repository ships with a **dual-license model** matching the BugOut Index:

- [`LICENSE.md`](../LICENSE.md) — **GNU Affero General Public License v3.0** for open-source use. Any hosted derivative must publish source under the same terms.
- [`COMMERCIAL_LICENSE.md`](../COMMERCIAL_LICENSE.md) — separate commercial license required for closed-source integration, paid SaaS, or ad/membership-supported sites. Contact: adam.w.montville@gmail.com.

Before the repo is made public and before GitHub Pages is enabled:

1. **Enable GitHub Pages using the GitHub Actions source.** In Settings → Pages, set **Source** to "GitHub Actions" (not "Deploy from a branch"). The workflow at `.github/workflows/pages.yml` uploads `site/` as the Pages artifact whenever `site/**` changes on `main`. GitHub's branch-and-folder Pages source only accepts `/` or `/docs`, which is why this project uses the Actions path — it lets `site/` stay a separate top-level folder from `docs/`. Confirm the site loads at `https://adammontville.github.io/american-dream-reality-index/` and that `assets/adri_timeseries.json` is fetchable.
2. **Confirm the ADRI wordmark is unencumbered.** A quick USPTO TESS search for "American Dream Reality Index" plus a general search for prior public use is inexpensive and worth doing before the site has a public URL.
3. **Change repository visibility to Public** (Settings → General → Change visibility).
4. **Only after** the site is verified: consider enabling branch protection on `main` and adding Issues templates for methodology feedback.

## 6. Failure modes to watch for

- **BJS release delay.** Incarceration is the slowest indicator. If yearend prison figures for reference year *t* have not published by Q4 of *t*+1, the pipeline will carry forward one year and annotate the ADRI record. If a second year passes with no publication, drop the indicator per METHODOLOGY.md §5.2 and expect Safety domain scores to be renormalized across the remaining active domains.
- **NAEP scale break.** The digital-administration transition (field test 2025) may declare a scale break. If NCES publishes a definitive break, treat it as a MAJOR version bump per METHODOLOGY.md §6.2 and re-anchor the indicator.
- **SPM XLSX schema drift.** METHODOLOGY.md §4 calls this out as medium-risk. If a new release changes the sheet layout, the manual update instructions in `data/raw/manual/README.md` still apply — the human updater is responsible for pulling the right cell and updating the CSV. There is no automated SPM parser.
- **UF Election Lab file layout.** VEP CSV format has shifted year to year in the past. The manual CSV path makes this a per-cycle human check rather than a scripted parse.
