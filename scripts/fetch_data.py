"""
fetch_data.py — Retrieve raw source data for each ADRI indicator.

Behavior by indicator kind:

  * fetch_kind == "manual": no automated fetch. The file already lives at
    data/raw/manual/<indicator_id>.csv and must be updated by hand when
    the primary source (PDF, XLSX, or manual extract) publishes a new
    vintage. This script simply logs its presence.

  * fetch_kind == "api": if the required environment variable(s) are set,
    call the source API and write a refreshed CSV to
    data/raw/api_cache/<indicator_id>.csv. If credentials are missing or
    the request fails, log a warning and leave the existing cached CSV in
    place so the pipeline can still run.

Environment variables recognized:

  FRED_API_KEY       — St. Louis Fed FRED API (indicators 5, 7)
  CENSUS_API_KEY     — U.S. Census Bureau API (indicators 2, 8)
                       (Census requests without a key are rate-limited but
                        work for small volumes; the key is recommended.)

The Socrata CDC endpoint (indicator 3, life expectancy) is public and needs
no key. CDC WONDER (indicator 4) requires an XML POST that is fragile
enough to remain manual in v0.1 — see METHODOLOGY.md §4.

Design rule: this script must never crash on a network failure. It writes
a clear warning line and returns non-zero only if *no* raw data is
available for any API-backed indicator.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import sys
from datetime import date
from pathlib import Path
from typing import Callable
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError

from config import INDICATORS, RAW_DIR, ensure_dirs, indicator_by_id

log = logging.getLogger("fetch_data")

USER_AGENT = "adri-fetch/0.1 (+https://github.com/AdamMontville/american-dream-reality-index)"


# ---------------------------------------------------------------------------
# Small HTTP helper. Deliberately stdlib-only to keep dependencies minimal.
# ---------------------------------------------------------------------------

def _http_get(url: str, timeout: int = 30) -> bytes:
    req = urlrequest.Request(url, headers={"User-Agent": USER_AGENT})
    with urlrequest.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return resp.read()


def _write_csv_with_header(
    path: Path,
    indicator: dict,
    rows: list[tuple[int, float]],
    extra_note: str = "",
) -> None:
    """Write a raw-cache CSV with the standard provenance header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        f.write(f"# indicator: {indicator['name']}\n")
        f.write(f"# source: {indicator['source']}\n")
        f.write(f"# vintage: {date.today().isoformat()} (auto-fetched)\n")
        if extra_note:
            for line in extra_note.splitlines():
                f.write(f"# {line}\n")
        w = csv.writer(f)
        w.writerow(["year", "value"])
        for y, v in sorted(rows):
            w.writerow([y, v])


# ---------------------------------------------------------------------------
# Per-indicator fetchers. Each returns True on success, False on skip/fail.
# ---------------------------------------------------------------------------

def _fetch_fred(series_id: str) -> list[tuple[int, float]]:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise RuntimeError("FRED_API_KEY not set")
    url = (
        "https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={api_key}&file_type=json"
    )
    payload = json.loads(_http_get(url))
    rows: list[tuple[int, float]] = []
    monthly: dict[int, list[float]] = {}
    for obs in payload.get("observations", []):
        d = obs.get("date", "")
        v_raw = obs.get("value", ".")
        if v_raw in (".", "", None):
            continue
        try:
            v = float(v_raw)
        except ValueError:
            continue
        try:
            y = int(d[:4])
        except ValueError:
            continue
        monthly.setdefault(y, []).append(v)
    for y, vals in monthly.items():
        # If a series is truly annual FRED will have one obs per year;
        # if monthly (LNS12300060), take the calendar-year mean per §5.3.
        rows.append((y, sum(vals) / len(vals)))
    return rows


def fetch_real_median_household_income(indicator: dict) -> bool:
    try:
        rows = _fetch_fred("MEHOINUSA672N")
    except Exception as exc:  # noqa: BLE001
        log.warning("real_median_household_income: %s — keeping cached CSV", exc)
        return False
    _write_csv_with_header(
        RAW_DIR / "api_cache" / f"{indicator['id']}.csv",
        indicator,
        rows,
        extra_note=(
            "FRED series MEHOINUSA672N, one obs per year. Values in real "
            "dollars per FRED metadata."
        ),
    )
    log.info("real_median_household_income: refreshed (%d rows)", len(rows))
    return True


def fetch_prime_age_epop(indicator: dict) -> bool:
    try:
        rows = _fetch_fred("LNS12300060")
    except Exception as exc:  # noqa: BLE001
        log.warning("prime_age_epop: %s — keeping cached CSV", exc)
        return False
    _write_csv_with_header(
        RAW_DIR / "api_cache" / f"{indicator['id']}.csv",
        indicator,
        rows,
        extra_note=(
            "FRED series LNS12300060 (monthly SA); annualized by arithmetic "
            "mean of monthly values per METHODOLOGY.md §5.3."
        ),
    )
    log.info("prime_age_epop: refreshed (%d rows)", len(rows))
    return True


def _fetch_census(url: str) -> list[list[str]]:
    api_key = os.environ.get("CENSUS_API_KEY", "")
    sep = "&" if "?" in url else "?"
    if api_key:
        url = f"{url}{sep}key={api_key}"
    return json.loads(_http_get(url))


def fetch_bachelors_attainment(indicator: dict) -> bool:
    """ACS 1-Year Table S1501 percent bachelor's or higher, ages 25+.

    The specific variable name varies slightly by year; the S1501 subject
    table's national profile row for 25+ bachelor's-or-higher percent is
    stable enough to fetch year by year.
    """
    latest_year = date.today().year - 1
    rows: list[tuple[int, float]] = []
    for y in range(2010, latest_year + 1):
        if y == 2020:  # Census did not publish ACS 1-Year for 2020
            continue
        # S1501_C02_015E = percent bachelor's or higher, 25+ (verify per year)
        url = (
            f"https://api.census.gov/data/{y}/acs/acs1/subject"
            "?get=S1501_C02_015E&for=us:1"
        )
        try:
            payload = _fetch_census(url)
            header, row = payload[0], payload[1]
            idx = header.index("S1501_C02_015E")
            rows.append((y, float(row[idx])))
        except Exception as exc:  # noqa: BLE001
            log.warning(
                "bachelors_attainment %d: %s — skipping this year", y, exc
            )
            continue
    if not rows:
        log.warning("bachelors_attainment: no rows fetched — keeping cached CSV")
        return False
    _write_csv_with_header(
        RAW_DIR / "api_cache" / f"{indicator['id']}.csv",
        indicator,
        rows,
        extra_note="ACS 1-Year S1501_C02_015E (percent bachelor's or higher, 25+).",
    )
    log.info("bachelors_attainment: refreshed (%d rows)", len(rows))
    return True


def fetch_gini(indicator: dict) -> bool:
    latest_year = date.today().year - 1
    rows: list[tuple[int, float]] = []
    for y in range(2010, latest_year + 1):
        if y == 2020:
            continue
        url = (
            f"https://api.census.gov/data/{y}/acs/acs1"
            "?get=B19083_001E&for=us:1"
        )
        try:
            payload = _fetch_census(url)
            header, row = payload[0], payload[1]
            idx = header.index("B19083_001E")
            rows.append((y, float(row[idx])))
        except Exception as exc:  # noqa: BLE001
            log.warning("gini %d: %s — skipping this year", y, exc)
            continue
    if not rows:
        log.warning("gini: no rows fetched — keeping cached CSV")
        return False
    _write_csv_with_header(
        RAW_DIR / "api_cache" / f"{indicator['id']}.csv",
        indicator,
        rows,
        extra_note="ACS 1-Year B19083_001E (national Gini).",
    )
    log.info("gini: refreshed (%d rows)", len(rows))
    return True


def fetch_life_expectancy(indicator: dict) -> bool:
    """CDC Socrata dataset w9j2-ggv5: U.S. life expectancy by year/race/sex.

    Filters to the national all-races both-sexes rows.
    """
    url = (
        "https://data.cdc.gov/resource/w9j2-ggv5.json"
        "?$limit=50000&race=All%20Races&sex=Both%20Sexes"
    )
    try:
        payload = json.loads(_http_get(url))
    except Exception as exc:  # noqa: BLE001
        log.warning("life_expectancy: %s — keeping cached CSV", exc)
        return False
    rows: list[tuple[int, float]] = []
    for r in payload:
        try:
            y = int(r.get("year"))
            v = float(r.get("average_life_expectancy") or r.get("life_expectancy"))
        except (TypeError, ValueError):
            continue
        rows.append((y, v))
    if not rows:
        log.warning("life_expectancy: parsed 0 rows — keeping cached CSV")
        return False
    _write_csv_with_header(
        RAW_DIR / "api_cache" / f"{indicator['id']}.csv",
        indicator,
        rows,
        extra_note=(
            "Socrata dataset w9j2-ggv5, filtered to All Races × Both Sexes. "
            "Provisional values may be present; the processing step should "
            "prefer the most recent final vintage where the two overlap."
        ),
    )
    log.info("life_expectancy: refreshed (%d rows)", len(rows))
    return True


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

FETCHERS: dict[str, Callable[[dict], bool]] = {
    "real_median_household_income": fetch_real_median_household_income,
    "prime_age_epop": fetch_prime_age_epop,
    "bachelors_attainment_25plus": fetch_bachelors_attainment,
    "gini_household_income": fetch_gini,
    "life_expectancy_at_birth": fetch_life_expectancy,
}


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    ensure_dirs()

    any_ok = False
    any_api = False

    for ind in INDICATORS:
        if ind["fetch_kind"] == "manual":
            path = RAW_DIR / "manual" / f"{ind['id']}.csv"
            if path.exists():
                log.info("%s: manual vintage of record at %s", ind["id"], path)
            else:
                log.warning(
                    "%s: manual raw file missing at %s — pipeline will treat "
                    "this indicator as unavailable",
                    ind["id"],
                    path,
                )
            continue

        any_api = True
        fn = FETCHERS.get(ind["id"])
        if fn is None:
            log.warning("%s: no fetcher registered — keeping cached CSV", ind["id"])
            continue
        ok = fn(ind)
        any_ok = any_ok or ok

    if any_api and not any_ok:
        log.warning(
            "No API indicator refreshed. Pipeline will use cached raw files. "
            "Set FRED_API_KEY and CENSUS_API_KEY (and check network) to refresh."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
