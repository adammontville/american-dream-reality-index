# Design Notes — American Dream Reality Index

Working notes to accompany [METHODOLOGY.md](METHODOLOGY.md). This file captures the reasoning behind design choices, alternative approaches considered, and open questions to revisit in future versions.

---

## 1. Framing decisions

### 1.1 Why "reality" and not "greatness"

The *Newsroom* McAvoy monologue is the emotional anchor for this project, but "greatness" is not a measurable construct. The ADRI substitutes a narrower, testable claim: **structural conditions correlated with the plausibility of prosperity and mobility**. The word "reality" is a deliberate signal that this is a factual scorecard, not an argument about virtue.

### 1.2 Two-pillar definition of the Dream

We define the American Dream as **prosperity + mobility**:
- *Prosperity* = a broadly-shared, stable material floor (income, employment, poverty).
- *Mobility* = the plausibility of improving one's position across a lifetime and across generations.

This mirrors the framing in the Aspen Institute / Brookings / Chetty et al. literature and lets us distinguish between "level" indicators (median income, life expectancy) and "structural" indicators (education, incarceration) that enable those levels over time. Every indicator in §3 of the methodology is labeled either *Enabling*, *Prosperity*, or *Mobility*.

### 1.3 What we intentionally left out

- **Subjective measures** (Gallup optimism, life-satisfaction). Structural, not psychological.
- **Housing affordability.** Important, but there is no widely-accepted single measure with the stability we require. Candidate for v0.2 (§4).
- **Wealth and net worth.** Same reason as housing — Fed SCF is triennial and hard to align with an annual composite.
- **Environmental measures** (air quality, climate exposure). Real structural factors, but outside the American-Dream framing that motivated this project.
- **Race, gender, and geographic disaggregations.** The index is national. A future version could publish parallel domain sub-scores for subpopulations without changing the headline number.

## 2. Indicator selection reasoning

### 2.1 Education

- **NAEP** is the gold-standard achievement measure, biennial, with a stable scale since the early 1990s. Grade 8 is preferred over grade 4 because 8th-grade achievement is a stronger predictor of downstream outcomes. Math + reading composite (equal-weight average of scale scores) gives one indicator that spans both literacy and numeracy.
- **Bachelor's attainment (25+)** is the education *stock* measure — how educated the adult population currently is, not just how well today's students test. Together, NAEP and attainment cover both quality (NAEP) and quantity/depth (attainment).
- **High school ACGR was rejected** because the series only starts in SY2010–11 (~14 years by 2026), it saturates near the top of its scale for many states, and the two indicators above already cover the domain.

### 2.2 Health

- **Life expectancy at birth** is the single best summary of population health.
- **Overdose mortality** was added because it is the only U.S. life-expectancy input that has moved decisively in structural terms over the past decade. It captures a piece of health that life expectancy alone smooths over.
- **Infant mortality was rejected** as too correlated with life expectancy to add signal.

### 2.3 Prosperity

- **Real median household income** covers level.
- **Supplemental Poverty Measure** covers the bottom of the distribution. It is preferred over the Official Poverty Measure because it incorporates taxes, near-cash transfers, medical out-of-pocket costs, and geographic cost of living — closer to a real measure of material hardship.
- **Prime-age (25–54) employment-to-population ratio** is the labor-utilization indicator, chosen deliberately over the headline unemployment rate to avoid the labor-force-exit problem (people who stop looking disappear from the unemployment rate but not the EPOP). This mirrors the BugOut Index's incubating Labor Utilization approach.

### 2.4 Opportunity — the mobility problem

The best direct mobility measurements — Raj Chetty et al., *Fading American Dream*, the Opportunity Atlas — are not maintained on an annual cadence. Using them as live indicators would violate the "regularly updated" rule and give us a series that stops updating after one release. So the index uses **Gini as an indirect mobility proxy**, on the basis of the Great Gatsby Curve literature. This is a **known compromise**:

- Gini measures current-year inequality, not mobility itself.
- The Great Gatsby link is a cross-country finding, not a within-U.S. law.
- A change in Gini does not straightforwardly imply a change in intergenerational mobility.

**Replacement candidate**: if Opportunity Insights, Census, or another source ever publishes a maintained annual mobility series, that indicator is the leading candidate to replace Gini here.

**Static benchmark option**: we may separately publish the last available Chetty et al. absolute-mobility snapshot on the site as historical context, clearly labeled as a static research release rather than an index input.

### 2.5 Civic — why turnout, and only turnout

Ideal civic-quality indicators would include press freedom, corruption perception, and rule-of-law measures. All three preferred sources (RSF, Transparency International, WJP Rule of Law Index) have significant reproducibility or comparability problems:

- **RSF**: PDF-only, no bulk file; 2013 methodology break.
- **Transparency International CPI**: 2012 methodology overhaul severs pre/post-2012 comparability; no API.
- **WJP Rule of Law Index**: annual, but scores are not directly comparable across years without WJP's own re-scaling; also not machine-readable in a stable way.

VEP turnout is the most machine-readable, methodologically stable civic indicator available. It is genuinely a partial measure of institutional health — turnout can rise for reasons unrelated to institutional quality (e.g., mobilization) — which is why the civic-domain weight is 0.10 rather than 0.20. Adding a stable second civic indicator is a v0.2 priority.

### 2.6 Safety — why incarceration, not violent crime

The natural pair would be violent crime + incarceration. The FBI's UCR→NIBRS transition in 2021 caused a documented, severe coverage discontinuity that has not fully resolved as of 2026. Publishing a national violent-crime rate through that transition would require either (a) mixing sources with different definitions or (b) accepting a coverage-driven artifact. Neither is acceptable for a slow structural index.

Incarceration alone is retained because it is stable, has a very long consistent history, and is a well-established structural condition affecting mobility (Western & Pettit 2010; Wakefield & Wildeman 2013). Violent crime is a leading v0.2 re-add candidate once NIBRS coverage stabilizes and a 5+ year clean run is available.

## 3. Normalization: why fixed anchors, not rolling percentiles

Composite indexes commonly use one of three approaches:

1. **Rolling percentile / z-score against a moving window.** Easy to compute, always well-distributed. But a stable index reading no longer means anything absolute — a "60" in 2028 is not the same as a "60" in 2015.
2. **Rolling percentile against the full history.** Better, but the index still drifts as the reference window grows.
3. **Fixed anchors** (min–max against pre-specified L and U). Every value is on the same absolute scale forever. New readings can go above 100 or below 0, so the score is clipped.

We chose (3) because the whole point is to enable *long-run comparison* of structural conditions. The cost is that anchors must be chosen carefully once and then changed only via a MAJOR version bump (with full recomputation of history).

**Anchor selection heuristic** (to be documented per-indicator in Thread 2):
- Lower anchor \( L \): the worst plausible U.S. condition, typically drawn from a domestic historical low, a comparable stressed-country reading, or a documented distress threshold.
- Upper anchor \( U \): a strong-condition target, typically drawn from a peer-country ceiling (OECD leaders) or a documented domestic peak.

Anchors will be recorded in each processed indicator file's header (`data/processed/<indicator>.json`) and referenced in `METHODOLOGY.md` Appendix A.

## 4. Version 0.2 candidates (do not implement in Thread 2)

These are the leading additions or replacements when the index matures:

- **Housing cost burden** (share of households paying >30% of income on housing, ACS Table B25070/B25091). Would rebalance the Prosperity domain. Stable ACS source, easy to add. **Do not add in v0.1**; needs its own weighting rationale.
- **Violent crime rate** once NIBRS coverage is stable for 5+ years — re-add to the Safety domain and rebalance to two indicators.
- **Direct mobility indicator** if a maintained annual series appears (Opportunity Insights, Census, or IRS statistics of income). Replace Gini or add alongside it in the Opportunity domain.
- **A second civic indicator** — the WJP Rule of Law Index, Freedom House Freedom in the World, or the V-Dem Liberal Democracy Index — chosen for machine-readability and comparability rather than journalistic prominence. Bring Civic to 0.15 or 0.20 once it has real dual measurement.
- **Mental-health morbidity** in the Health domain (e.g., NSDUH serious mental illness prevalence), once a stable series is confirmed.
- **State and demographic sub-indexes** — same indicators, same weights, computed for the 50 states + DC and for selected demographic slices. Not a change to the headline number; an addition to the site.

## 5. Source-verification reference

This is the working source-verification table that informed §3 of the methodology. It is retained here (rather than in `METHODOLOGY.md`) because it is a reference dataset, not a methodological rule.

*Update this section whenever a source URL, cadence, or vintage changes.*

### Core indicators — retained

| # | Indicator | Landing page | Access URL | Latest vintage (mid-2026) | Cadence | Machine-readable? |
|---|---|---|---|---|---|---|
| 1 | NAEP gr.8 math + reading | [nationsreportcard.gov](https://www.nationsreportcard.gov/) | [NAEP Data Service API](https://www.nationsreportcard.gov/DataService/GetAdhocData.aspx) | 2024 (results Jan 2025); 2026 admin underway | Biennial | JSON API |
| 2 | Bachelor's attainment 25+ (ACS S1501) | [data.census.gov S1501](https://data.census.gov/table/ACSST1Y2024.S1501) | [Census API](https://api.census.gov/data/2024/acs/acs1/subject) | 2024 ACS 1-Year | Annual | REST API + CSV |
| 3 | Life expectancy at birth | [NVSS Life Expectancy](https://www.cdc.gov/nchs/nvss/life-expectancy.htm) | [data.cdc.gov Socrata dataset](https://data.cdc.gov/api/views/w9j2-ggv5/rows.csv?accessType=DOWNLOAD) | 2023 final; 2024 provisional | Annual | Socrata CSV/JSON API |
| 4 | Overdose mortality (age-adjusted) | [NVSS Drug Overdose](https://www.cdc.gov/nchs/nvss/drug-overdose-deaths.htm) | [CDC WONDER API](https://wonder.cdc.gov/wonder/help/wonder-api.html); [VSRR provisional CSV](https://healthdata.gov/resource/abjp-5k3g.csv) | 2024 final (23.1/100k, [NCHS DB 549](https://www.cdc.gov/nchs/products/databriefs/db549.htm), Jan 2026) | Annual final; monthly provisional | WONDER XML API + Socrata |
| 5 | Real median household income | [FRED MEHOINUSA672N](https://fred.stlouisfed.org/series/MEHOINUSA672N) | [FRED API](https://fred.stlouisfed.org/docs/api/fred/) | 2024 ($83,730, released Sep 2025) | Annual | FRED REST API |
| 6 | Supplemental Poverty Measure | [Census SPM](https://www.census.gov/topics/income-poverty/data/tables.html) | [SPM datasets](https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/) | 2024 (Report P60-287) | Annual | XLSX/CSV |
| 7 | Prime-age EPOP (25-54) | [FRED LNS12300060](https://fred.stlouisfed.org/series/LNS12300060) | [BLS API](https://data.bls.gov/dataViewer/view/timeseries/LNS12300060) / FRED API | Latest monthly | Monthly | BLS + FRED APIs |
| 8 | Gini index (ACS B19083) | [data.census.gov B19083](https://data.census.gov/table/ACSDT1Y2024.B19083) | [Census API](https://api.census.gov/data/2024/acs/acs1) `B19083_001E` | 2024 (0.4809 national) | Annual | REST API |
| 9 | VEP turnout | [UF Election Lab](https://election.lab.ufl.edu/voter-turnout/) | [Data downloads](https://election.lab.ufl.edu/data-downloads/turnoutdata/) | 2024 general (~63.5%) | Biennial | CSV/Excel |
| 10 | Incarceration rate | [BJS](https://bjs.ojp.gov/) | [Prisoners](https://bjs.ojp.gov/library/publications/prisoners-2023-statistical-tables) + [Jails](https://bjs.ojp.gov/library/publications/jails-report-series-2024-preliminary-data-release) statistical tables (PDF); microdata via [NACJD](https://www.icpsr.umich.edu/web/NACJD/series/9) | Prisons yearend 2023; Jails midyear 2024 preliminary | Annual | PDF-primary; microdata as SPSS/Stata/CSV |

### Indicators evaluated and not used in v0.1

| Indicator | Source | Why not used |
|---|---|---|
| ACGR (high school graduation) | NCES / EDFacts, [Digest Table 219.46](https://nces.ed.gov/programs/digest/d23/tables/dt23_219.46.asp) | Series only ~14 years old; NAEP + attainment already cover education |
| Official Poverty Measure | Census P60 series | Superseded by SPM |
| Infant mortality | CDC NCHS Linked Birth/Infant Death | Too correlated with life expectancy |
| Opportunity Insights absolute mobility | [opportunityinsights.org/data](https://opportunityinsights.org/data/) | Not a maintained annual series; static 2016 release |
| EIG Distressed Communities Index | [eig.org/dci-hub](https://eig.org/dci-hub/) | Composite of variables already in the ADRI; would double-count |
| RSF Press Freedom Index | [rsf.org/en/index](https://rsf.org/en/index) | PDF/HTML only, no bulk file; 2013 methodology break |
| Transparency International CPI | [transparency.org/en/cpi](https://www.transparency.org/en/cpi/2025) | 2012 methodology overhaul severs comparability; no API |
| FBI UCR/NIBRS violent crime | [Crime Data Explorer](https://cde.ucr.cjis.gov/) | 2021 NIBRS transition caused severe coverage discontinuity; re-add candidate for v0.2 |

## 6. Open questions to resolve in Thread 2 or later

1. **Exact anchor values** for each indicator. Anchor selection is the single most consequential remaining design choice; get it wrong and the index either saturates or never moves.
2. **NAEP composite construction.** Simple average of math and reading scale scores, or standardized composite? The scales are similar in range, so a simple average is probably fine, but this should be verified against NAGB documentation.
3. **VEP handling of midterms vs. presidentials.** Options: (a) use whichever is most recent; (b) use only presidential-year turnout; (c) publish two variants. Presidential turnout is higher and less noisy — leaning toward (b), but revisit in Thread 2.
4. **Incarceration retrieval fallback.** BJS PDFs are the primary source; NACJD microdata is the secondary. Confirm which is more reliable in practice once we try to automate an actual pull.
5. **Publishing an equal-weight variant.** Committed in §5.4 of the methodology. Confirm site-side that both are visible without letting the design-weighted one appear "official" in a way that hides the sensitivity.
6. **Should the index publish a confidence indicator?** A simple "1 = all indicators fresh; lower if any indicator was carried forward or its domain reweighted" flag would help readers gauge the current release's quality. Design this in Thread 2 alongside the JSON schema for the time series.

## 7. Naming

"McAvoy Index" is the emotional/branding working title; `american-dream-reality-index` is the descriptive working name used in this repo. A public release under any character-derived name requires a trademark review. Alternative names considered so far have been described as lacking character; new suggestions are open.
