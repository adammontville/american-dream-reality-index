"""
process_indicators.py — Read raw indicator CSVs, clean them, and write one
canonical processed JSON per indicator to data/processed/.

Each processed file has this schema:

  {
    "id": "<indicator id>",
    "name": "<human name>",
    "domain": "<domain>",
    "direction": +1 | -1,
    "unit": "<unit>",
    "frequency": "annual" | "biennial" | "monthly",
    "source": "<primary source URL>",
    "anchors": {
        "low": <L>,
        "high": <U>,
        "source": "<anchor rationale>"
    },
    "raw_path": "<repo-relative path to source CSV>",
    "vintage_note": "<free text pulled from the CSV header>",
    "series": [
        {"year": 2010, "value": <raw value>, "carried_forward": false},
        ...
    ]
  }

Processing rules mirror METHODOLOGY.md:

  * Biennial indicators are stored as-is with no interpolation. Carry-forward
    for non-vintage years is applied only in compute_index.py where a target
    reference year is known (§5.2, §5.3).
  * Monthly indicators (only #7 prime-age EPOP in v0.1) arrive already
    annualized in the raw CSV — the fetcher averages them and the CSV
    contains one value per year. We do NOT re-average here.
  * No normalization happens in this step. Normalization lives in
    compute_index.py so anchors and directions are applied at composite time.
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

from config import (
    INDICATORS,
    PROCESSED_DIR,
    RAW_DIR,
    REPO_ROOT,
    ensure_dirs,
)

log = logging.getLogger("process_indicators")


def _read_csv_with_header(path: Path) -> tuple[list[tuple[int, float]], str]:
    """Read a `# ...` header CSV; return (rows, header_note)."""
    header_lines: list[str] = []
    data_lines: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                header_lines.append(line.rstrip("\n"))
            else:
                data_lines.append(line)
    reader = csv.DictReader(data_lines)
    rows: list[tuple[int, float]] = []
    for r in reader:
        try:
            y = int(r["year"])
            v = float(r["value"])
        except (KeyError, TypeError, ValueError):
            continue
        rows.append((y, v))
    rows.sort()
    return rows, "\n".join(header_lines)


def _raw_path_for(indicator: dict) -> Path:
    if indicator["fetch_kind"] == "manual":
        return RAW_DIR / "manual" / f"{indicator['id']}.csv"
    return RAW_DIR / "api_cache" / f"{indicator['id']}.csv"


def process_one(indicator: dict) -> dict | None:
    raw_path = _raw_path_for(indicator)
    if not raw_path.exists():
        log.warning(
            "%s: raw file %s missing — indicator will be marked unavailable",
            indicator["id"],
            raw_path,
        )
        return None

    rows, header_note = _read_csv_with_header(raw_path)
    if not rows:
        log.warning("%s: raw file %s parsed 0 rows", indicator["id"], raw_path)
        return None

    processed = {
        "id": indicator["id"],
        "name": indicator["name"],
        "domain": indicator["domain"],
        "direction": indicator["direction"],
        "unit": indicator["unit"],
        "frequency": indicator["frequency"],
        "source": indicator["source"],
        "anchors": {
            "low": indicator["anchor_low"],
            "high": indicator["anchor_high"],
            "source": indicator["anchor_source"],
        },
        "raw_path": str(raw_path.relative_to(REPO_ROOT)),
        "vintage_note": header_note,
        "series": [
            {"year": y, "value": v, "carried_forward": False} for y, v in rows
        ],
    }
    return processed


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    ensure_dirs()

    ok = 0
    for ind in INDICATORS:
        processed = process_one(ind)
        if processed is None:
            continue
        out_path = PROCESSED_DIR / f"{ind['id']}.json"
        out_path.write_text(json.dumps(processed, indent=2) + "\n", encoding="utf-8")
        log.info(
            "%s: wrote %d observations to %s",
            ind["id"],
            len(processed["series"]),
            out_path.relative_to(REPO_ROOT),
        )
        ok += 1

    log.info("processed %d/%d indicators", ok, len(INDICATORS))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
