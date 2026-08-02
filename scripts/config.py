"""
Central configuration for the American Dream Reality Index pipeline.

All indicator definitions, anchors, weights, and source URLs live here.
Every value is grounded in docs/METHODOLOGY.md. If you change one of these
values, bump the methodology version per METHODOLOGY.md §6.2.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "index"
SITE_DIR = REPO_ROOT / "site"
SITE_ASSETS_DIR = SITE_DIR / "assets"
DOCS_DIR = REPO_ROOT / "docs"

# ---------------------------------------------------------------------------
# Methodology version pin (see METHODOLOGY.md §6.2)
# ---------------------------------------------------------------------------

METHODOLOGY_VERSION = "0.1.2"

# ---------------------------------------------------------------------------
# Indicator definitions
#
# Each indicator declares:
#   id            : short machine name used in filenames and JSON keys
#   number        : the numeric id used in METHODOLOGY.md §3.1
#   name          : human label
#   domain        : one of the six domains in METHODOLOGY.md §5.4
#   direction     : +1 if higher raw = better, -1 if higher raw = worse
#   anchor_low    : L in the normalization formula (see §5.1)
#   anchor_high   : U in the normalization formula
#   anchor_source : short note explaining why L and U were chosen
#   unit          : human-readable unit label
#   frequency     : annual | biennial | monthly
#   source        : URL of the primary source
#   fetch_kind    : one of {api, manual}. `manual` means the seed CSV
#                   under data/raw/manual/ is the vintage-of-record until an
#                   automated fetch is implemented.
#
# Anchor values here are v0.1 initial anchors. NOTES.md §6.1 marks final
# anchor selection as an open question; these are defensible starting points,
# documented per indicator, chosen so that (a) historical U.S. values sit
# clearly inside [L, U] and (b) L and U reflect stressed vs. strong structural
# conditions per the METHODOLOGY.md §5.1 heuristic.
# ---------------------------------------------------------------------------

INDICATORS: list[dict] = [
    {
        "id": "naep_g8_composite",
        "number": 1,
        "name": "NAEP grade-8 math + reading composite",
        "domain": "Education",
        "direction": +1,
        "anchor_low": 250.0,
        "anchor_high": 290.0,
        "anchor_source": (
            "Grade-8 NAEP scale scores have historically sat in the 260–285 "
            "band on the national assessment. L=250 marks a clearly stressed "
            "level below any observed U.S. reading since the current scale; "
            "U=290 marks a strong ceiling above historical U.S. highs, "
            "consistent with top-performing OECD peer averages when crosswalked."
        ),
        "unit": "scale-score average (math+reading, grade 8)",
        "frequency": "biennial",
        "source": "https://www.nationsreportcard.gov/DataService/GetAdhocData.aspx",
        "fetch_kind": "manual",
    },
    {
        "id": "bachelors_attainment_25plus",
        "number": 2,
        "name": "Bachelor's degree attainment, age 25+",
        "domain": "Education",
        "direction": +1,
        "anchor_low": 20.0,
        "anchor_high": 45.0,
        "anchor_source": (
            "U.S. adult bachelor's attainment was ~20% in the late 1980s and "
            "reached ~37–38% by 2024. L=20 anchors on the domestic historical "
            "low of the modern series; U=45 anchors above current U.S. levels "
            "at a plausible OECD-leader ceiling (e.g., Canada, Korea, Ireland "
            "for tertiary attainment adjusted for definitional differences)."
        ),
        "unit": "percent of population 25+",
        "frequency": "annual",
        "source": "https://api.census.gov/data/2024/acs/acs1/subject",
        "fetch_kind": "api",
    },
    {
        "id": "life_expectancy_at_birth",
        "number": 3,
        "name": "Life expectancy at birth",
        "domain": "Health",
        "direction": +1,
        "anchor_low": 74.0,
        "anchor_high": 84.0,
        "anchor_source": (
            "U.S. life expectancy at birth dipped to ~76.4 in 2021 and has "
            "sat between 76 and 79 since 2000. L=74 anchors below the pandemic "
            "trough as a stressed-domestic floor; U=84 anchors near the "
            "top-of-OECD ceiling (Japan, Switzerland ~84)."
        ),
        "unit": "years",
        "frequency": "annual",
        "source": "https://data.cdc.gov/api/views/w9j2-ggv5/rows.csv",
        "fetch_kind": "api",
    },
    {
        "id": "overdose_mortality_age_adjusted",
        "number": 4,
        "name": "Drug overdose mortality, age-adjusted",
        "domain": "Health",
        "direction": -1,
        "anchor_low": 4.0,
        "anchor_high": 35.0,
        "anchor_source": (
            "Age-adjusted overdose deaths per 100,000 rose from ~4 in 1999 to "
            "~32.6 in 2022 and eased to ~23–24 in 2024. L=4 anchors on the "
            "1999 domestic floor (representing a favorable ceiling on the "
            "0–100 score); U=35 anchors above the 2022 peak so a return to "
            "peak-crisis conditions maps near 0."
        ),
        "unit": "deaths per 100,000, age-adjusted",
        "frequency": "annual",
        "source": "https://wonder.cdc.gov/wonder/help/wonder-api.html",
        "fetch_kind": "manual",
    },
    {
        "id": "real_median_household_income",
        "number": 5,
        "name": "Real median household income",
        "domain": "Prosperity",
        "direction": +1,
        "anchor_low": 55000.0,
        "anchor_high": 90000.0,
        "anchor_source": (
            "Real median household income (FRED MEHOINUSA672N, 2024 CPI-U-RS "
            "dollars) ranged ~$56k in 1994 to ~$83.7k in 2024. L=55000 "
            "anchors below the modern-series floor; U=90000 anchors above "
            "the 2024 high as a plausible near-term ceiling."
        ),
        "unit": "real dollars",
        "frequency": "annual",
        "source": "https://fred.stlouisfed.org/series/MEHOINUSA672N",
        "fetch_kind": "api",
    },
    {
        "id": "supplemental_poverty_rate",
        "number": 6,
        "name": "Supplemental Poverty Measure rate",
        "domain": "Prosperity",
        "direction": -1,
        "anchor_low": 6.0,
        "anchor_high": 18.0,
        "anchor_source": (
            "SPM ranged from ~7.8% in 2021 (with expanded transfers) to "
            "~15–16% in the 2010s. L=6 anchors below the modern low; U=18 "
            "anchors above the historical modern high."
        ),
        "unit": "percent",
        "frequency": "annual",
        "source": (
            "https://www2.census.gov/programs-surveys/"
            "supplemental-poverty-measure/datasets/spm/"
        ),
        "fetch_kind": "manual",
    },
    {
        "id": "prime_age_epop",
        "number": 7,
        "name": "Prime-age (25–54) employment-to-population ratio",
        "domain": "Prosperity",
        "direction": +1,
        "anchor_low": 70.0,
        "anchor_high": 82.0,
        "anchor_source": (
            "Prime-age EPOP (FRED LNS12300060, annual mean of monthly SA "
            "values) has ranged ~74.8 in 2010 to ~80.9 in 2000 and ~80.9 "
            "in 2024. L=70 anchors below any modern-series reading; U=82 "
            "anchors above historical peaks as a strong-labor-utilization "
            "ceiling."
        ),
        "unit": "percent",
        "frequency": "monthly",
        "source": "https://fred.stlouisfed.org/series/LNS12300060",
        "fetch_kind": "api",
    },
    {
        "id": "gini_household_income",
        "number": 8,
        "name": "Gini index of household income",
        "domain": "Opportunity",
        "direction": -1,
        "anchor_low": 0.35,
        "anchor_high": 0.50,
        "anchor_source": (
            "ACS Gini (B19083) has sat between 0.46 and 0.49 nationally in "
            "recent years. L=0.35 anchors on a peer-OECD floor (roughly the "
            "range of the more equal advanced economies); U=0.50 anchors "
            "above the U.S. modern high as a stressed ceiling."
        ),
        "unit": "Gini coefficient (0–1)",
        "frequency": "annual",
        "source": "https://api.census.gov/data/2024/acs/acs1",
        "fetch_kind": "api",
    },
    {
        "id": "vep_turnout",
        "number": 9,
        "name": "Voter turnout of voting-eligible population (presidential)",
        "domain": "Civic",
        "direction": +1,
        "anchor_low": 50.0,
        "anchor_high": 75.0,
        "anchor_source": (
            "U.S. VEP presidential-year turnout has ranged ~51.7% (1996) to "
            "~66.6% (2020). L=50 anchors below the modern-series low; U=75 "
            "anchors above the modern high toward a peer-democracy ceiling. "
            "Per NOTES.md §6.3, this v0.1 uses presidential-year turnout "
            "carried forward to intervening midterm-only years."
        ),
        "unit": "percent (presidential-year VEP)",
        "frequency": "biennial",
        "source": "https://election.lab.ufl.edu/data-downloads/turnoutdata/",
        "fetch_kind": "manual",
    },
    {
        "id": "incarceration_rate_per_100k",
        "number": 10,
        "name": "Total incarceration rate per 100,000",
        "domain": "Safety",
        "direction": -1,
        "anchor_low": 150.0,
        "anchor_high": 750.0,
        "anchor_source": (
            "Combined prisons+jails per 100k peaked ~1000 in the late 2000s "
            "and has fallen to ~530–560 by 2022–2023. L=150 anchors near "
            "OECD-peer levels (e.g., Western Europe ~100–150); U=750 anchors "
            "below the historical U.S. peak so a return to that peak maps "
            "clearly toward the low end of the 0–100 score."
        ),
        "unit": "persons per 100,000 residents",
        "frequency": "annual",
        "source": "https://bjs.ojp.gov/",
        "fetch_kind": "manual",
    },
]

# ---------------------------------------------------------------------------
# Domain weights (see METHODOLOGY.md §5.4)
# ---------------------------------------------------------------------------

DOMAIN_WEIGHTS: dict[str, float] = {
    "Education": 0.20,
    "Health": 0.20,
    "Prosperity": 0.20,
    "Opportunity": 0.15,
    "Civic": 0.10,
    "Safety": 0.15,
}

# Sanity check on module import
assert abs(sum(DOMAIN_WEIGHTS.values()) - 1.0) < 1e-9, \
    "DOMAIN_WEIGHTS must sum to 1.0"


def indicators_by_domain() -> dict[str, list[dict]]:
    """Return {domain_name: [indicator dict, ...]} for composite computation."""
    out: dict[str, list[dict]] = {d: [] for d in DOMAIN_WEIGHTS}
    for ind in INDICATORS:
        out[ind["domain"]].append(ind)
    return out


def indicator_by_id(indicator_id: str) -> dict:
    for ind in INDICATORS:
        if ind["id"] == indicator_id:
            return ind
    raise KeyError(f"Unknown indicator id: {indicator_id}")


def ensure_dirs() -> None:
    for p in (RAW_DIR, PROCESSED_DIR, INDEX_DIR, SITE_DIR, SITE_ASSETS_DIR):
        p.mkdir(parents=True, exist_ok=True)
