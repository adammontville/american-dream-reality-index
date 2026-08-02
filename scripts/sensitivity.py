#!/usr/bin/env python3
"""Univariate anchor-sensitivity sweep for the ADRI.

For each indicator, perturb L (anchor_low) and U (anchor_high) by
+/- 10% of the span (U - L), one anchor at a time, holding all other
indicators at their baseline anchors. Recompute the full 2010-2024
published series (with the METHODOLOGY sec 5.3.1 publication threshold
applied) and record |Delta ADRI| vs. the baseline for each year.

Outputs
-------
docs/sensitivity/v0.1.1-sweep.csv
    Long-format sweep results with one row per (indicator, anchor,
    direction, year).
docs/sensitivity/v0.1.1-summary.csv
    Ranked summary: for each (indicator, anchor, direction) the
    mean and max |Delta ADRI| across published years.

The script does NOT modify data/index/ or site/assets/; it only reads
data/processed/ and writes to docs/sensitivity/.

See METHODOLOGY.md sec 5.1 for the normalization formula this
probes.
"""

from __future__ import annotations

import copy
import csv
import json
import logging
from pathlib import Path

import config
import compute_index

log = logging.getLogger("sensitivity")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
# Quiet compute_index's per-year suppression logs during the sweep.
logging.getLogger("compute_index").setLevel(logging.WARNING)


PERTURBATION_FRACTION = 0.10  # +/- 10% of the (U - L) span, per anchor


def _compute_series_from_current_config() -> dict[int, float]:
    """Read whatever compute_index.INDICATORS points at right now and return
    {year: adri} for the published series."""
    ts = compute_index.compute_timeseries()
    return {row["year"]: row["adri"] for row in ts["series"]}


def _apply_indicators(perturbed: list[dict]) -> None:
    """Point both config.INDICATORS and compute_index.INDICATORS at a new list.

    compute_index imported INDICATORS by name (`from config import INDICATORS`)
    so we must rebind both references. Also flush the domain-map cache since
    it captures INDICATORS at first call.
    """
    config.INDICATORS[:] = perturbed
    compute_index.INDICATORS[:] = perturbed


def main() -> None:
    # Snapshot the baseline (deep copy so we can restore exactly).
    baseline_indicators = copy.deepcopy(config.INDICATORS)
    baseline_series = _compute_series_from_current_config()
    published_years = sorted(baseline_series)
    log.info(
        "baseline: %d published years %d..%d",
        len(published_years), published_years[0], published_years[-1],
    )

    rows: list[dict] = []
    for ind_index, ind in enumerate(baseline_indicators):
        span = ind["anchor_high"] - ind["anchor_low"]
        step = PERTURBATION_FRACTION * span
        for anchor_key in ("anchor_low", "anchor_high"):
            for sign, label in ((+1, "plus"), (-1, "minus")):
                delta = sign * step
                perturbed = copy.deepcopy(baseline_indicators)
                perturbed[ind_index][anchor_key] += delta
                p_ind = perturbed[ind_index]
                if p_ind["anchor_high"] - p_ind["anchor_low"] <= 0:
                    log.warning(
                        "skipping %s %s %s: perturbation collapses span",
                        ind["id"], anchor_key, label,
                    )
                    continue
                _apply_indicators(perturbed)
                try:
                    perturbed_series = _compute_series_from_current_config()
                finally:
                    _apply_indicators(baseline_indicators)  # always restore
                for y in published_years:
                    if y not in perturbed_series:
                        continue
                    d = perturbed_series[y] - baseline_series[y]
                    rows.append({
                        "indicator_id": ind["id"],
                        "indicator_number": ind["number"],
                        "domain": ind["domain"],
                        "direction": ind["direction"],
                        "anchor": anchor_key,
                        "sign": label,
                        "delta_value": round(delta, 6),
                        "year": y,
                        "baseline_adri": round(baseline_series[y], 4),
                        "perturbed_adri": round(perturbed_series[y], 4),
                        "delta_adri": round(d, 4),
                        "abs_delta_adri": round(abs(d), 4),
                    })

    # Sanity-check: restore left INDICATORS pointing at baseline.
    assert config.INDICATORS[0]["anchor_low"] == baseline_indicators[0]["anchor_low"], "baseline not restored"

    out_dir = config.REPO_ROOT / "docs" / "sensitivity"
    out_dir.mkdir(parents=True, exist_ok=True)

    sweep_path = out_dir / "v0.1.1-sweep.csv"
    with sweep_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    log.info("wrote %d rows -> %s", len(rows), sweep_path)

    # Summary: per (indicator, anchor, sign), mean and max |Delta ADRI|
    summary: dict[tuple, dict] = {}
    for r in rows:
        key = (r["indicator_id"], r["indicator_number"], r["domain"], r["anchor"], r["sign"])
        s = summary.setdefault(key, {"abs": [], "signed": [], "years_affected": 0})
        s["abs"].append(r["abs_delta_adri"])
        s["signed"].append(r["delta_adri"])
        s["years_affected"] += 1

    summary_rows = []
    for (iid, num, dom, anchor, sign), agg in summary.items():
        mean_abs = sum(agg["abs"]) / len(agg["abs"])
        max_abs = max(agg["abs"])
        mean_signed = sum(agg["signed"]) / len(agg["signed"])
        summary_rows.append({
            "indicator_id": iid,
            "indicator_number": num,
            "domain": dom,
            "anchor": anchor,
            "sign": sign,
            "years_affected": agg["years_affected"],
            "mean_abs_delta_adri": round(mean_abs, 4),
            "max_abs_delta_adri": round(max_abs, 4),
            "mean_signed_delta_adri": round(mean_signed, 4),
        })
    summary_rows.sort(key=lambda r: r["max_abs_delta_adri"], reverse=True)
    summary_path = out_dir / "v0.1.1-summary.csv"
    with summary_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        w.writeheader()
        w.writerows(summary_rows)
    log.info("wrote %d summary rows -> %s", len(summary_rows), summary_path)

    log.info("Top 15 anchor perturbations by max |Delta ADRI|:")
    for r in summary_rows[:15]:
        log.info(
            "  %-32s #%2d %-11s %s %-5s  mean=%.3f  max=%.3f",
            r["indicator_id"], r["indicator_number"], r["domain"],
            r["anchor"], r["sign"],
            r["mean_abs_delta_adri"], r["max_abs_delta_adri"],
        )


if __name__ == "__main__":
    main()
