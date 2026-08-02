"""
compute_index.py — Read processed indicator JSONs, normalize with fixed
anchors, and compute the ADRI composite and per-domain sub-scores for every
reference year where at least one indicator has data.

Output: data/index/adri_timeseries.json

Schema:

  {
    "methodology_version": "0.1.0",
    "generated_at": "2026-08-02T...Z",
    "notes": "<short human note>",
    "series": [
      {
        "year": 2010,
        "adri": 62.3,
        "adri_equal_weight": 60.1,
        "confidence": 1.0,
        "domain_scores": {
          "Education": 71.2, ...
        },
        "domain_weights_used": {
          "Education": 0.20, ...
        },
        "indicator_scores": {
          "naep_g8_composite": {
            "raw": 273.5,
            "raw_vintage_year": 2011,
            "normalized": 58.75,
            "carried_forward": false,
            "carry_forward_years": 0
          },
          ...
        },
        "annotations": [
          "carried_forward: naep_g8_composite (biennial; last vintage 2011)"
        ]
      },
      ...
    ]
  }

Rules implemented (all from METHODOLOGY.md):

  * §5.1  Fixed-anchor min-max normalization with directionality and
          clipping to [0, 100].
  * §5.2  One-year carry-forward for missing values. Biennial indicators
          are allowed to carry forward up to one year past their vintage.
  * §5.3  Annual reference year; monthly and biennial indicators are
          resolved to a single value.
  * §5.4  Domain sub-scores are equal-weighted means of component scores.
          Composite is a weighted sum of domain sub-scores. If a domain
          has zero components available even with carry-forward, its
          weight is redistributed proportionally across the other domains.
  * §7.5  Equal-weight variant is published alongside the design-weighted
          composite so readers can see weight sensitivity.

Confidence flag (from NOTES.md §6.6):

  confidence = 1.0 if all indicators have a fresh (uncarried) value in
  the reference year; lower proportionally for each indicator that is
  carried forward or missing. This is a simple heuristic, not a formal
  statistical quantity.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from config import (
    DOMAIN_WEIGHTS,
    INDEX_DIR,
    INDICATORS,
    METHODOLOGY_VERSION,
    PROCESSED_DIR,
    ensure_dirs,
    indicators_by_domain,
)

log = logging.getLogger("compute_index")


def _load_processed() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for ind in INDICATORS:
        path = PROCESSED_DIR / f"{ind['id']}.json"
        if not path.exists():
            log.warning("%s: processed file missing at %s", ind["id"], path)
            continue
        out[ind["id"]] = json.loads(path.read_text(encoding="utf-8"))
    return out


def _series_dict(processed: dict) -> dict[int, float]:
    return {obs["year"]: obs["value"] for obs in processed["series"]}


def _max_carry_for(indicator: dict) -> int:
    """How many missing years an indicator is allowed to carry forward.

    METHODOLOGY.md §5.2 sets the general rule: at most one *reference*
    year of missing data. For indicators that publish less often than
    annually, the rule becomes: fill the natural gap between vintages,
    plus at most one additional year past the last vintage.

      * annual / monthly → 1 year of carry-forward.
      * biennial (NAEP)  → 2 years (one gap year + one grace year).
      * VEP presidential→ 4 years. NOTES.md §6.3 chose presidential-only
        turnout as v0.1's civic indicator; the natural cycle is four
        years, so we allow carry-forward through the full inter-election
        window. Every non-presidential year is annotated with the vintage
        year and carry count in the ADRI record.
    """
    if indicator["id"] == "vep_turnout":
        return 4
    if indicator["frequency"] == "biennial":
        return 2
    return 1


def _value_for_year(
    series: dict[int, float],
    year: int,
    max_carry: int,
) -> tuple[float | None, int | None, int]:
    """Return (value, vintage_year, carry_years) for a reference year."""
    if year in series:
        return series[year], year, 0
    for k in range(1, max_carry + 1):
        if (year - k) in series:
            return series[year - k], year - k, k
    return None, None, 0


def _normalize(value: float, low: float, high: float, direction: int) -> float:
    if high == low:
        return 0.0
    if direction == +1:
        s = 100.0 * (value - low) / (high - low)
    else:
        s = 100.0 * (high - value) / (high - low)
    if s < 0.0:
        return 0.0
    if s > 100.0:
        return 100.0
    return s


def _all_reference_years(processed: dict[str, dict]) -> list[int]:
    years: set[int] = set()
    for proc in processed.values():
        years.update(obs["year"] for obs in proc["series"])
    return sorted(years)


# A reference year is only published if it clears this minimum coverage bar.
# See METHODOLOGY.md §5.3: the reference year is the most recent year for
# which every indicator has a provisional-or-better vintage. We can't
# enforce "every indicator" strictly (biennial gaps, real-world missing
# data), so v0.1 requires every domain to have at least one component and
# the overall coverage to be at least this threshold. Years below the bar
# are computed internally but suppressed from the published time series so
# the site does not surface composites built from one or two indicators.
MIN_INDICATOR_COVERAGE = 0.6  # 6 of 10 indicators must be present or carried


def _compute_one_year(
    year: int,
    processed: dict[str, dict],
) -> dict | None:
    domain_map = indicators_by_domain()

    indicator_scores: dict[str, dict] = {}
    domain_components: dict[str, list[float]] = {d: [] for d in DOMAIN_WEIGHTS}
    annotations: list[str] = []
    total_indicators = len(INDICATORS)
    missing_or_carried = 0

    for ind in INDICATORS:
        proc = processed.get(ind["id"])
        if proc is None:
            missing_or_carried += 1
            annotations.append(f"missing: {ind['id']}")
            continue
        series = _series_dict(proc)
        value, vintage, carry = _value_for_year(
            series, year, max_carry=_max_carry_for(ind)
        )
        if value is None:
            missing_or_carried += 1
            annotations.append(f"missing: {ind['id']}")
            continue

        normalized = _normalize(
            value, ind["anchor_low"], ind["anchor_high"], ind["direction"]
        )
        indicator_scores[ind["id"]] = {
            "raw": value,
            "raw_vintage_year": vintage,
            "normalized": round(normalized, 3),
            "carried_forward": carry > 0,
            "carry_forward_years": carry,
        }
        domain_components[ind["domain"]].append(normalized)
        if carry > 0:
            missing_or_carried += 1
            annotations.append(
                f"carried_forward: {ind['id']} "
                f"({ind['frequency']}; last vintage {vintage})"
            )

    # Drop domains with zero components; redistribute their weights
    active_domain_scores: dict[str, float] = {}
    for domain, comps in domain_components.items():
        if not comps:
            annotations.append(f"domain_dropped: {domain} (no components)")
            continue
        active_domain_scores[domain] = sum(comps) / len(comps)

    if not active_domain_scores:
        return None

    # Design weights (renormalized over active domains)
    active_weights_design = {d: DOMAIN_WEIGHTS[d] for d in active_domain_scores}
    z = sum(active_weights_design.values())
    active_weights_design = {d: w / z for d, w in active_weights_design.items()}
    adri = sum(
        active_weights_design[d] * active_domain_scores[d]
        for d in active_domain_scores
    )

    # Equal-weight variant (§7.5): every active domain weighted 1/n
    n = len(active_domain_scores)
    equal_w = 1.0 / n
    adri_equal = sum(equal_w * s for s in active_domain_scores.values())

    confidence = max(
        0.0,
        min(1.0, 1.0 - (missing_or_carried / max(1, total_indicators))),
    )

    return {
        "year": year,
        "adri": round(adri, 2),
        "adri_equal_weight": round(adri_equal, 2),
        "confidence": round(confidence, 2),
        "domain_scores": {
            d: round(s, 2) for d, s in active_domain_scores.items()
        },
        "domain_weights_used": {
            d: round(w, 4) for d, w in active_weights_design.items()
        },
        "indicator_scores": indicator_scores,
        "annotations": annotations,
    }


def compute_timeseries() -> dict:
    processed = _load_processed()
    if not processed:
        raise SystemExit("No processed indicators found; run process_indicators.py first.")

    years = _all_reference_years(processed)
    series: list[dict] = []
    for y in years:
        row = _compute_one_year(y, processed)
        if row is None:
            continue
        # Publication threshold: every domain must have at least one
        # component and coverage must clear MIN_INDICATOR_COVERAGE.
        if len(row["domain_scores"]) < len(DOMAIN_WEIGHTS):
            log.info(
                "suppressing year %d: only %d/%d domains covered",
                y, len(row["domain_scores"]), len(DOMAIN_WEIGHTS),
            )
            continue
        if row["confidence"] < MIN_INDICATOR_COVERAGE:
            log.info(
                "suppressing year %d: confidence %.2f below threshold %.2f",
                y, row["confidence"], MIN_INDICATOR_COVERAGE,
            )
            continue
        series.append(row)

    return {
        "methodology_version": METHODOLOGY_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": (
            "ADRI (American Dream Reality Index) v0.1. See docs/METHODOLOGY.md "
            "for indicator definitions, anchors, normalization, and weighting. "
            "Confidence is a coarse freshness heuristic; see docs/NOTES.md §6.6."
        ),
        "domain_weights": DOMAIN_WEIGHTS,
        "indicators": [
            {
                "id": ind["id"],
                "name": ind["name"],
                "domain": ind["domain"],
                "direction": ind["direction"],
                "unit": ind["unit"],
                "frequency": ind["frequency"],
                "anchor_low": ind["anchor_low"],
                "anchor_high": ind["anchor_high"],
                "source": ind["source"],
            }
            for ind in INDICATORS
        ],
        "series": series,
    }


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    ensure_dirs()
    payload = compute_timeseries()

    out_path = INDEX_DIR / "adri_timeseries.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # Convenience CSV for humans and spreadsheets.
    csv_path = INDEX_DIR / "adri_timeseries.csv"
    with csv_path.open("w", encoding="utf-8") as f:
        f.write("year,adri,adri_equal_weight,confidence\n")
        for row in payload["series"]:
            f.write(
                f"{row['year']},{row['adri']},{row['adri_equal_weight']},{row['confidence']}\n"
            )

    if payload["series"]:
        latest = payload["series"][-1]
        log.info(
            "wrote %d rows; latest year=%d adri=%.2f (equal-weight %.2f, confidence %.2f)",
            len(payload["series"]),
            latest["year"],
            latest["adri"],
            latest["adri_equal_weight"],
            latest["confidence"],
        )
    else:
        log.warning("no rows computed")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
