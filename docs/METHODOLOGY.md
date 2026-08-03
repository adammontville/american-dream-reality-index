# American Dream Reality Index — Methodology

**Version:** 1.0.0
**Status:** First stable release. Indicator set, weights, anchors, publication threshold, and output schema are now considered the public API of the ADRI.
**Last updated:** 2026-08-03

---

## 1. Purpose and scope

The American Dream Reality Index (ADRI) is a small, transparent composite of **U.S. structural conditions** that affect how plausible the American Dream — durable prosperity plus intergenerational mobility — is in practice for the median resident.

The ADRI tracks *enabling conditions*, not outcomes for any individual and not a country's "greatness." Concretely:

- **It measures** whether the country is currently well set up to produce broadly-shared prosperity and mobility: how well children are educated, how long and healthily people live, whether households are economically stable, whether communities are functional, whether civic institutions work, and whether the criminal-justice footprint is proportionate.
- **It does not measure** individual success, national identity, cultural virtue, subjective optimism, or the outcome of any particular person's American Dream.
- **It is a model, not a probability.** A higher ADRI does not mean any specific person is more likely to succeed; it means the structural terrain is, on the chosen measures, more favorable.

The ADRI is deliberately **slow-moving** and **backward-looking**. Most inputs update annually; a few update biennially or quarterly. Fast-moving events belong in other products (e.g., the BugOut Index's Current Signals layer), not here.

## 1.1 What we mean by "the American Dream"

The American Dream has never had a single agreed definition. This index adopts a specific one: the structural conditions under which a **median American resident** can reasonably expect material security, basic educational access, health and longevity, political voice, and freedom from a punitive institutional floor. These are the conditions that historically preceded the property-ownership, family-formation, and generational-mobility outcomes most often associated with the phrase "American Dream" in 20th-century framings.

**What autonomy and state coercion look like in the ADRI.** Two of the ten indicators speak directly to the individual's relationship with the state: the **incarceration rate per 100,000**, which is the most direct measurable signal of state physical coercion at a population scale, and **VEP turnout**, which measures political voice. These are partial signals of a concept that deserves broader measurement than the ADRI can support with sound public data alone. A reader who prioritizes autonomy and freedom-from-coercion as central to the American Dream should treat these two indicators as necessary but not sufficient, and read the ADRI alongside more coercion-focused indices such as the [BugOut Index](https://adammontville.github.io/bugout-index/).

**What the ADRI does not measure.** Cultural belonging, subjective flourishing, physical safety at the personal level, environmental quality, community cohesion, or the specific 20th-century markers (single-earner household sufficiency, single-family homeownership at working-class wages, guaranteed upward class mobility across generations). A reader who defines the American Dream around any of these should treat the ADRI as adjacent but incomplete.

**What the ADRI cannot resolve.** Whether these structural conditions are the *right* things to measure. Younger observers, in particular, increasingly define the American Dream in terms of security and autonomy rather than accumulation and ownership — a reframing the ADRI's indicator set partially reflects (through incarceration and VEP turnout) but does not fully capture. The ADRI's indicator set was designed to be **generationally neutral on framing but specific on measurement** — it measures the material substrate that most competing definitions still depend on, without endorsing any single cultural definition of what a "good life" looks like on top of that substrate.

## 1.2 The 0–100 scale, in practice

The ADRI is bounded 0–100 by construction, but the endpoints of that range are theoretical, not observed. A score of 100 would require every indicator to simultaneously reach its most-favorable-observed anchor value; a score of 0 would require every indicator to simultaneously reach its worst-observed anchor value. Neither has happened in the observation window, and neither is expected to happen in a mixed economy where indicators trade off against each other.

Across the 2010–2024 observation window, published design-weighted ADRI values have ranged from **34.9 (2012) to 43.9 (2024)**. Real-world scores are expected to continue falling within a narrower band than the full 0–100 range. Readers are encouraged to reason from the observed range rather than from the theoretical endpoints.

## 2. Design principles

1. **Robustness over cleverness.** Prefer indicators with long, stable, publicly-documented series over novel but fragile ones.
2. **Methodology before code.** All computation rules must be specified in this document before any script is written.
3. **Epistemic humility.** Every score is versioned, every methodology change is annotated, and the site publishes limitations alongside the number.
4. **Reproducibility.** Any snapshot of the index can be recomputed from raw source files and this document alone.
5. **Static architecture.** All artifacts (raw data, processed data, index time series, site) are plain files hosted on GitHub Pages; no backend service is required to view or verify the index.
6. **Small n.** A modest indicator count (target: 10, hard ceiling: 12) beats a large one for transparency and maintainability.

## 3. Indicator set

The ADRI uses **10 core indicators** spanning six domains. Each is drawn from a widely-used, publicly-documented series maintained by a government agency or a well-established civil-society organization.

### 3.1 Final indicator table

| # | Indicator | Domain | Type | Source (Agency) | Access | Frequency | Direction | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | NAEP grade-8 math & reading composite | Education | Enabling | NCES / NAGB | [NAEP Data Service API](https://www.nationsreportcard.gov/DataService/GetAdhocData.aspx) (JSON) | Biennial | Higher = better | Average of gr.8 math + reading scale scores; stable scale since 1990/1992 |
| 2 | Bachelor's degree attainment, age 25+ | Education | Enabling | Census Bureau (ACS 1-Year, Table S1501) | [Census API](https://api.census.gov/data/2024/acs/acs1/subject) (JSON) | Annual | Higher = better | Adult educational stock; percent with bachelor's degree or higher |
| 3 | Life expectancy at birth | Health | Enabling | CDC / NCHS (NVSS) | [Socrata CSV/JSON](https://data.cdc.gov/api/views/w9j2-ggv5/rows.csv) | Annual | Higher = better | Final NVSS series; provisional data ignored for the index |
| 4 | Drug overdose mortality, age-adjusted | Health | Enabling | CDC / NCHS (NVSS via WONDER) | [CDC WONDER API](https://wonder.cdc.gov/wonder/help/wonder-api.html) (XML) | Annual | Lower = better | ICD-10 drug-induced deaths; consistent coding since 1999 |
| 5 | Real median household income | Prosperity | Prosperity | Census (CPS ASEC), hosted on FRED | [FRED API](https://fred.stlouisfed.org/docs/api/fred/) `MEHOINUSA672N` | Annual | Higher = better | Real dollars; deflator-seam noted (§7.4) |
| 6 | Supplemental Poverty Measure rate | Prosperity | Prosperity | Census Bureau (Report P60 series) | [Census SPM datasets](https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/) (XLSX/CSV) | Annual | Lower = better | Preferred over the Official Poverty Measure; reflects taxes, transfers, and geographic cost |
| 7 | Prime-age (25–54) employment-to-population ratio | Prosperity | Prosperity | BLS (CPS), hosted on FRED | [FRED API](https://fred.stlouisfed.org/docs/api/fred/) `LNS12300060` | Monthly (annualized) | Higher = better | Annualized to a single yearly value (see §5.3) |
| 8 | Gini index of household income | Opportunity | Mobility | Census Bureau (ACS 1-Year, Table B19083) | [Census API](https://api.census.gov/data/2024/acs/acs1) `B19083_001E` | Annual | Lower = better | Inequality serves as an indirect mobility proxy; see §3.3 |
| 9 | Voter turnout of voting-eligible population (VEP) | Civic | Enabling | U.S. Elections Project (McDonald / UF Election Lab) | [CSV/Excel download](https://election.lab.ufl.edu/data-downloads/turnoutdata/) | Biennial | Higher = better | General-election years only; midterms and presidentials tracked separately (see §5.4) |
| 10 | Total incarceration rate per 100,000 residents | Safety | Enabling | BJS (DOJ) | [Prisoners](https://bjs.ojp.gov/library/publications/prisoners-2023-statistical-tables) + [Jails](https://bjs.ojp.gov/library/publications/jails-report-series-2024-preliminary-data-release) statistical tables (PDF; microdata via [NACJD](https://www.icpsr.umich.edu/web/NACJD/series/9)) | Annual | Lower = better | Prisons + jails combined; excludes probation/parole |

**Types:**
- *Enabling* = structural conditions that make prosperity and mobility more likely.
- *Prosperity* = current level of economic well-being.
- *Mobility* = the plausibility of moving across the distribution over time. Gini is a *proxy* — see §3.3.

### 3.2 Indicators considered and rejected

| Indicator | Reason rejected |
|---|---|
| High school Adjusted Cohort Graduation Rate (ACGR) | Series only ESSA-mandated since SY2010–11; ~14 years is at the edge of the continuity threshold, and NAEP + bachelor's attainment already cover the education domain adequately |
| Official Poverty Measure | Superseded by the Supplemental Poverty Measure, which incorporates taxes, transfers, and geographic cost of living |
| Infant mortality rate | Highly correlated with life expectancy at birth; keeping one health-outcome indicator plus one behavioral-mortality indicator (overdose deaths) is enough |
| Opportunity Insights absolute mobility (Chetty et al. 2016) | Not a maintained annual series — flagship data have not been refreshed with new birth cohorts since original 2016 release. Structurally different from the other 16 candidates. Documented in NOTES.md for potential future use as a **static benchmark**, not a live indicator |
| EIG Distressed Communities Index | Composite of variables already in the ADRI (poverty, employment, income); paid license for the full dataset; would double-count |
| RSF Press Freedom Index | PDF/HTML only, no bulk machine-readable file; 2013 methodology break; harder to make reproducible |
| Transparency International CPI | Same reproducibility caveat plus a 2012 methodology break that severs pre/post-2012 comparability |
| FBI UCR / NIBRS violent crime rate | 2021 NIBRS transition caused a severe coverage discontinuity; keeping incarceration alone as the safety-domain indicator is more stable. NIBRS-only violent crime is an obvious re-add candidate once coverage stabilizes (see §7.4) |

### 3.3 Why Gini stands in for mobility

The intent is to measure mobility as one of the two pillars of the American Dream. The best available *direct* mobility measurements (Chetty et al., Raj Chetty and Nathaniel Hendren's Opportunity Atlas, *Fading American Dream*) are not maintained on an annual cadence, so they cannot serve as a live indicator without breaking the "regularly updated" rule.

Gini is used as an **indirect mobility proxy** on the basis of the "Great Gatsby Curve" literature (Krueger 2012; Corak 2013), which finds a robust cross-country negative correlation between income inequality and intergenerational income mobility. This is a proxy, not a mobility measure. Its limitations are stated openly in §7 and on the site.

If Opportunity Insights ever publishes a maintained annual series, or the Census releases a comparable federal mobility series, this indicator is the leading candidate for replacement.

## 4. Feasibility assessment

For each core indicator, the retrieval plan and maintenance burden are:

| # | Indicator | Retrieval plan | Maintenance burden | Risk |
|---|---|---|---|---|
| 1 | NAEP gr.8 math + reading | JSON API pull, keyed by subject × grade × year × jurisdiction=National | Biennial script run after each main-assessment release | Low. Watch for the ongoing digital-administration transition (2025+ field test) for scale comparability |
| 2 | ACS bachelor's attainment | REST API call, one variable per year | Annual; run after ACS 1-Year release (~September) | Low |
| 3 | Life expectancy | Socrata CSV pull; filter to national, all-race, both-sex | Annual; run after final NVSS mortality data (12–18 month lag) | Low |
| 4 | Overdose mortality | CDC WONDER XML POST (national aggregate) | Annual (final); optional VSRR quarterly refresh via Socrata | Medium — WONDER API is documented but XML-based and cranky. Fallback: NCHS Data Briefs (annual PDF, manual extract) |
| 5 | Real median household income | FRED API, one series, one call | Annual after Income & Poverty report (~September) | Low. Deflator-seam noted (§7.4) |
| 6 | SPM rate | Direct XLSX download from Census SPM datasets page; parse fixed sheet | Annual; run after P60 Income & Poverty report | Medium — file structure is stable but not schema-guaranteed. Manual regression test on each update |
| 7 | Prime-age employment-population ratio | FRED API, one series | Monthly; index uses the calendar-year average of monthly values | Low |
| 8 | Gini | Census API `B19083_001E` | Annual; run after ACS 1-Year release | Low |
| 9 | VEP turnout | Excel/CSV from UF Election Lab site; parse fixed sheet | Biennial (Nov even years); update after certification (~Dec/Jan) | Medium — spreadsheet layout can shift year to year. Manual regression test on each update |
| 10 | Incarceration rate | Two PDF-primary series: BJS Prisoners (yearend) + BJS Jails (midyear preliminary or full). Text extract or ICPSR/NACJD microdata download. | Annual, but manual — PDFs are the primary release. Preferred fallback: NACJD dataset when available | High — PDF extraction is fragile and BJS publication schedule is irregular. Also has substantial release lag |

**Handling the two high-risk paths** (indicators 6 and 10):
- **SPM:** archive each release's XLSX under `data/raw/spm/<vintage>.xlsx`; run a schema check against a saved header signature; fail loudly rather than silently on layout change.
- **Incarceration:** primary path is manual PDF extract with a saved parse note per vintage; secondary path is the NACJD SPSS/Stata microdata refresh, which is more stable but slower to appear. If neither is available for the current vintage, carry forward the prior year with an explicit `stale_years` annotation (§5.5).

## 5. Normalization, weighting, and composite

### 5.1 Normalization

Every raw indicator is transformed to a **0–100 score** where higher always means "better for the Dream." The transformation is a **fixed-anchor min–max rescaling**, not a rolling percentile.

For an indicator with value \( x \), direction \( d \in \{+1, -1\} \), lower anchor \( L \), and upper anchor \( U \):

- If \( d = +1 \) (higher raw = better): \( s = 100 \cdot (x - L) / (U - L) \)
- If \( d = -1 \) (higher raw = worse): \( s = 100 \cdot (U - x) / (U - L) \)

Then \( s \) is **clipped to [0, 100]**. Values outside the anchors are capped, not extrapolated.

**Anchors are fixed once at index launch** using a defensible external reference for each indicator (documented per-indicator in `NOTES.md` and in each `data/processed/<indicator>.json` header). Fixed anchors are chosen so that:

- \( L \) = a value clearly indicating a stressed structural condition (e.g., a domestic historical low, or a peer-country floor).
- \( U \) = a value clearly indicating a strong structural condition (e.g., an aspirational peer-country ceiling or a documented domestic high).

Fixed anchors preserve **inter-year comparability**: a 5-point ADRI change means the same thing in 2028 as in 2015. This is the main reason we do **not** use rolling percentile or z-score normalization.

Anchor revisions are versioned. A change to any anchor is a major-version bump (§6.2), and prior series are re-computed against the new anchors and republished side-by-side.

### 5.2 Outliers and missing values

- **Outliers:** the clip to [0, 100] is the only outlier treatment. No winsorization, no trimming.
- **Missing values:** if an indicator has no vintage for the target reference year, the index carries forward the most recent prior value **for at most one reference year**, with the ADRI record annotated `carried_forward: <indicator>`. If a second consecutive year is missing, the domain-score aggregation (§5.4) omits that indicator and the omission is annotated. The composite formula (§5.4) handles this by renormalizing weights within the affected domain.
- **VEP presidential-cycle exception.** Indicator 9 (VEP turnout) is treated in this release as a presidential-only measure per NOTES.md §6.3, and is therefore permitted to carry forward for **up to four reference years** — the length of one presidential cycle. Applied literally, the one-year rule above would evict the Civic domain from every non-election year and suppress most reference years by §5.3.1. Every non-presidential year still receives the `carried_forward: vep_turnout` annotation. This exception is scoped to indicator 9 and does not extend to any other biennial or lower-frequency indicator (e.g., NAEP still gets at most the one-year grace). The exception is a candidate for removal in a MAJOR bump if a second civic indicator is added and VEP no longer needs a long carry-forward.
- **Definitional breaks:** documented per-indicator (§7.4). No mechanical adjustment; each break is annotated in the time series and — where appropriate — a re-computed pre-break series is published alongside.

### 5.3 Aligning frequencies to an annual reference year

The composite is computed **once per calendar year**, with the *reference year* being the most recent year for which every indicator has at least a provisional-or-better vintage.

- **Annual indicators** (2, 3, 5, 6, 8, 10): use the value for the reference year, as of the most recent final release.
- **Monthly indicator** (7, prime-age EPOP): annual value = arithmetic mean of the 12 monthly seasonally-adjusted values for the reference year.
- **Biennial indicators** (1 NAEP, 9 VEP turnout): use the most recent published biennial value at the time of the composite. Between biennial releases, the value is carried forward but the ADRI record annotates the vintage year on the indicator.

Because most inputs lag by 6–18 months, the ADRI for calendar year *t* is expected to be publishable in **Q4 of year *t*+1** at the earliest, and possibly year *t*+2 if BJS or NVSS is late.

The strict form of this rule — every indicator present with at least a provisional-or-better vintage — is the ideal. In practice, the historical series and any reference year may have gaps. §5.3.1 defines the minimum coverage a reference year must meet to be published.

### 5.3.1 Publication threshold

A reference year is **published** in the ADRI time series only if it meets **both** of the following coverage tests:

1. **Indicator coverage.** At least **6 of the 10 indicators** must have a value for the reference year, either from a direct vintage or from a carry-forward permitted by §5.2.
2. **Domain coverage.** Every one of the six domains must have at least one indicator with a value after carry-forward. If any domain has zero available indicators, the reference year is suppressed even if the indicator-count test passes.

When a reference year fails either test, the pipeline still computes its component scores internally, but the row is **omitted from the published time series** and logged with the reason. The row may be re-included in a later release once additional vintages become available (see §6.3 on source revisions).

The indicator-coverage threshold is exposed in code as the constant `MIN_INDICATOR_COVERAGE = 0.6` in `scripts/compute_index.py` so it can be tuned in a MAJOR version bump (§6.2) without further methodology changes. The domain-coverage test is not tunable.

**Rationale.** The 6/10 floor is a compromise between two failure modes. Requiring all 10 indicators (the strictest reading of §5.3) would suppress most pre-2010 reference years given the current indicator set and would give away legitimate signal in years where only a slow source (BJS, NAEP) is late. Publishing years with 1–2 indicators would produce a composite that is really a report on whichever indicators happened to arrive, with a confidence score too low to be useful. 6/10 with all six domains present is the point at which the composite still exercises every domain weight and every carry-forward is bounded.

Each published record also carries a **confidence** field (0–1) equal to the fraction of the 10 indicators that were directly measured for that reference year (i.e., not carried forward). Readers should treat records with confidence below ~0.7 with proportional skepticism.

### 5.4 Composite formula

Indicators are grouped into six **domains**. Each domain first produces a 0–100 domain sub-score as the equally-weighted mean of its component indicator scores. Domain sub-scores are then combined into the ADRI using **fixed domain weights**.

**Domains, components, and weights (initial v0.1 assignment):**

| Domain | Indicators | Domain weight |
|---|---|---|
| Education | 1 (NAEP), 2 (Bachelor's attainment) | 0.20 |
| Health | 3 (Life expectancy), 4 (Overdose mortality) | 0.20 |
| Prosperity | 5 (Real median income), 6 (SPM), 7 (Prime-age EPOP) | 0.20 |
| Opportunity | 8 (Gini, as mobility proxy) | 0.15 |
| Civic | 9 (VEP turnout) | 0.10 |
| Safety | 10 (Incarceration rate) | 0.15 |
| **Total** | | **1.00** |

Weights are **assigned by design intent**, not by statistical optimization. The rationale:

- Education, Health, and Prosperity each receive 0.20 because they are the three pillars most consistently supported by the empirical literature on economic mobility and the American-Dream framing (education as ladder, health as prerequisite, income as scaffold).
- Opportunity (Gini as mobility proxy) receives 0.15 rather than 0.20 because a single indirect proxy should carry less weight than a two- or three-indicator domain.
- Safety receives 0.15 because incarceration is a well-established structural condition affecting mobility (Western & Pettit 2010) but is a single indicator, so it does not warrant a full 0.20.
- Civic receives 0.10 because VEP turnout is a partial measure of civic-institution health, and the domain has only one indicator. It stays in the composite because civic quality is thematically central to the ADRI framing; it is down-weighted because the measurement is thinner than in other domains.

Let \( s_{d,i} \) be the 0–100 score of indicator \( i \) in domain \( d \), and \( n_d \) be the number of indicators in domain \( d \) with non-missing values. The domain score is:

\[
D_d = \frac{1}{n_d} \sum_{i=1}^{n_d} s_{d,i}
\]

If \( n_d = 0 \) (every indicator in the domain is missing beyond the one-year carry-forward), the domain's weight is redistributed proportionally across the other domains, and the ADRI record annotates the redistribution.

The composite is:

\[
\text{ADRI} = \sum_{d} w_d \cdot D_d
\]

with \( \sum_d w_d = 1 \) after any redistribution.

**Pseudocode for one reference year:**

```
def compute_adri(reference_year, indicator_series, anchors, domain_map, weights):
    domain_scores = {}
    for domain, indicators in domain_map.items():
        component_scores = []
        for ind in indicators:
            x = indicator_series[ind].value_for(reference_year, carry_forward_years=1)
            if x is None:
                continue
            L, U = anchors[ind].lower, anchors[ind].upper
            d = anchors[ind].direction  # +1 or -1
            raw = ((x - L) / (U - L)) if d == +1 else ((U - x) / (U - L))
            component_scores.append(clip(100 * raw, 0, 100))
        if component_scores:
            domain_scores[domain] = mean(component_scores)
    # Redistribute weights across the domains that have at least one component
    active = {d: weights[d] for d in domain_scores}
    z = sum(active.values())
    active = {d: w / z for d, w in active.items()}
    return sum(active[d] * domain_scores[d] for d in domain_scores)
```

## 6. Update cadence, versioning, and revisions

### 6.1 Cadence

- **Annual structural refresh** every Q4 of year *t*+1, once ACS, income/poverty, life expectancy, and overdose figures are all available for reference year *t*.
- **Interim refreshes** are permitted only when a source materially revises a prior-year value (e.g., ACS revision, BJS reclassification) or when a biennial indicator produces its next vintage (NAEP even years, VEP even years). Interim refreshes bump the patch version (§6.2).
- **No sub-annual composite.** The ADRI is not published quarterly. Component-level charts on the site may show monthly or quarterly detail (e.g., prime-age EPOP), but the composite itself remains annual.

### 6.2 Versioning

Every ADRI record and methodology change follows semantic versioning:

- **MAJOR** — any change that alters historical scores: anchor changes, weight changes, indicator additions or removals, definitional overhauls.
- **MINOR** — a new reference-year computation with no methodology change.
- **PATCH** — recomputation of an existing reference year due to source revision or a documented data-entry fix.

Every published index file (`data/index/adri_timeseries.json`) carries a `methodology_version` field pinning it to the git tag of `METHODOLOGY.md` in effect when it was computed. Old versions of both the methodology and the time series are retained; they are not overwritten.

### 6.3 Handling source revisions

When a primary source revises a prior-year value (e.g., Census re-releases an ACS estimate, BJS restates prisoner counts):

1. Store the raw revised file under `data/raw/<indicator>/<vintage>_r<revision-number>.<ext>`.
2. Rerun the composite for every affected reference year.
3. Publish the recomputed rows under a new PATCH version, alongside — not on top of — the prior rows.
4. Annotate each affected row with the source revision date and a short note.

## 7. Limitations and caveats

### 7.1 What the ADRI cannot tell you

- Whether *you personally* are more or less likely to achieve the American Dream.
- Whether the country is "better" or "worse" in any absolute or moral sense.
- What is causing any observed change.
- Anything at a state, county, or demographic-group level. The ADRI is national.

### 7.2 What the ADRI is likely to mis-weight

- **Civic quality** is thinly measured (one indicator, VEP turnout). Turnout is a partial signal for institutional health; it says nothing about press freedom, rule of law, or corruption. The civic domain weight is deliberately low as a result.
- **Mobility** is measured indirectly via Gini. This inherits the Great Gatsby Curve's known limitations: the cross-country inequality-mobility link is not necessarily a cross-time within-U.S. law.
- **Safety** covers only incarceration. Violent-crime rates are excluded during the NIBRS transition (§7.4); re-adding them is a planned v0.2 candidate once national NIBRS coverage stabilizes.
- **Health** covers longevity and overdose deaths. It excludes morbidity, mental-health outcomes, and access measures.

### 7.3 Data lag

The ADRI trails reality by 12–24 months. It is a **structural** measure. If you want a real-time picture, this is the wrong instrument.

### 7.3.1 Known indicator-level freshness limitations (as of v1.0.0)

Two indicators currently have known freshness limitations that the maintainer is aware of and evaluating for a future release:

- **Life expectancy at birth (indicator 3).** The FRED-hosted series (`SPDYNLE00INUSA`, sourced from World Bank) currently stops at 2018. CDC NCHS has published final and provisional life-expectancy figures for years beyond 2018, but they are not yet integrated into this pipeline. As a result, ADRI values for reference years 2019 and later use the 2018 life-expectancy value carried forward under the four-year carry-forward rule (§5.2 has a one-year default; life expectancy is not covered by the VEP presidential-cycle exception, and any use beyond one year is a known deviation being carried while the source-swap is evaluated). Switching to a CDC NCHS-direct source is a candidate change for a subsequent release.
- **Prime-age employment-to-population ratio (indicator 7).** This series is monthly at source. The pipeline currently annualizes whatever months are available, which means that in mid-year the most-recent "annual" value can reflect a partial year. This is by design as of v1.0.0: it makes the index more responsive to labor-market conditions than a strict full-year rule would allow, at the cost of introducing partial-year data into the most-recent point. Readers who prefer full-year values should look at the year prior to the latest for a full-year figure.

### 7.4 Documented discontinuities per indicator

| Indicator | Discontinuity | Handling |
|---|---|---|
| NAEP (1) | Ongoing digital-administration transition (field test 2025) may affect scale comparability | Monitor; annotate if NCES declares a break |
| Real median household income (5) | Deflator switch from R-CPI-U-RS to C-CPI-U within the FRED series | Minor; documented; no adjustment |
| SPM (6) | Methodology updates in 2019+ data; CPS income question redesign from 2013+ | Annotate on the site; recompute prior years if Census republishes historical SPM under a new definition |
| Prime-age EPOP (7) | None material | — |
| Incarceration (10) | Release lag; occasional definitional changes for jail population | Annotate; use most recent BJS definition |
| RSF Press Freedom (dropped) | 2013 methodology revision | N/A |
| Transparency International CPI (dropped) | 2012 methodology overhaul; pre/post-2012 scores not comparable | N/A |
| FBI UCR/NIBRS (dropped) | 2021 NIBRS transition caused a severe coverage drop | N/A; re-add candidate for v0.2 once coverage is stable |

### 7.5 Weighting is a choice

Weights in §5.4 are a design decision, not a fact. They embody a claim that education, health, and prosperity are equal-weight primary pillars, with mobility and safety half a step behind and civic quality further down. Reasonable people will disagree. The methodology commits to publishing:

- The composite under the current weights.
- An equal-weight variant (all six domains at 1/6) as a second series in the same file, so readers can see how sensitive the composite is to the weighting choice.

## 8. Reproducibility contract

Any ADRI value published on the site must be reproducible from:

1. This document, at the git tag pinned in the record's `methodology_version` field.
2. The raw source files under `data/raw/`, at the vintage pinned in each processed file's header.
3. The scripts under `scripts/` (to be written in Thread 2), at the same git tag.

If any of these three is missing, the ADRI value cannot be published.

---

## Appendix A — Indicator quick reference

Full source URLs, access notes, and vintage tracking are maintained in `../data/raw/<indicator>/README.md` (created per-indicator when Thread 2 begins retrieval work). This section is a locator, not a substitute for the source-verification reference in `NOTES.md`.

## Appendix B — Change log

- **v1.0.0 (2026-08-03)** — MAJOR. First stable release. The indicator set, domain weights, anchor values, publication threshold, and output schema are now considered the **public API** of the ADRI; future changes to these elements will require a major version bump with a documented rationale. This release adds:
  - A new §1.1 ("What we mean by the American Dream") that names the specific definition of the American Dream this index adopts, acknowledges the concepts it does not measure, and cross-references the BugOut Index as a complementary coercion-focused signal.
  - A new §1.2 ("The 0–100 scale, in practice") that documents the observable range of the design-weighted composite (34.9–43.9 across 2010–2024) and clarifies that the theoretical endpoints of the 0–100 scale are not expected to be reached in practice.
  - A new §7.3.1 documenting two known indicator-level freshness limitations (life expectancy stops at 2018 in the current FRED source; prime-age EPOP admits partial-year data in the most-recent point) that are candidates for follow-up work.

  This release also marks the first **fully-authoritative refresh** of the underlying data: all four API-backed indicators (real median household income, prime-age EPOP, bachelor's degree attainment, Gini) now pull directly from FRED and Census APIs rather than the seed CSVs bundled during initial development. As a result, the aggregate ADRI for reference year 2024 moved from **44.16 (v0.1.2 seed values)** to **43.86 (v1.0.0 authoritative values)**. The seed values were bundled to make the pipeline runnable without API credentials during initial development; they are no longer part of the reported series.

- **v0.1.2 (2026-08-02)** — MINOR. Added the VEP presidential-cycle carry-forward exception to §5.2 (up to four reference years for indicator 9 only). Closes the last methodology↔implementation gap flagged in v0.1.1. No score change: the reference implementation already carried VEP forward for four years; this revision only makes the methodology consistent with what the pipeline was already doing.
- **v0.1.1 (2026-08-02)** — MINOR. Added §5.3.1 formalizing the publication threshold used by the reference implementation (indicator coverage ≥ 6/10 and all six domains represented after carry-forward). Corrected a stale cross-reference in §5.2 (domain aggregation is defined in §5.4, not §5.3). One methodology↔implementation gap remained open at the time of this release: the reference implementation carried the VEP indicator forward for up to four years rather than the one year permitted by §5.2. Resolved in v0.1.2.
- **v0.1 (2026-08-02)** — Initial design draft. Indicator set frozen at 10 across six domains. Fixed-anchor min-max normalization, equal-within-domain aggregation, fixed domain weights (0.20/0.20/0.20/0.15/0.10/0.15). No computed values yet.
