"""
run_all.py — Orchestrate the full ADRI pipeline.

Steps:
  1. fetch_data.py         — refresh raw sources where possible; leave
                             manual and cached files as-is on failure.
  2. process_indicators.py — read raw CSVs, write per-indicator processed
                             JSON to data/processed/.
  3. compute_index.py      — normalize with fixed anchors, compute per-domain
                             sub-scores and the composite, write time series
                             to data/index/.
  4. render_site.py        — copy the time series into site/assets/ and
                             render docs/METHODOLOGY.md into
                             site/methodology.html.

Use `--skip-fetch` to skip network calls entirely (useful for CI or when
sources are down; the cached raw files will be used).
"""

from __future__ import annotations

import argparse
import logging
import sys

import fetch_data
import process_indicators
import compute_index
import render_site


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the ADRI pipeline end to end.")
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip fetch_data; use cached raw files as-is.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    log = logging.getLogger("run_all")

    if not args.skip_fetch:
        log.info("STEP 1/4 fetch_data")
        rc = fetch_data.main()
        if rc:
            log.warning("fetch_data returned %d; continuing with cached raw", rc)
    else:
        log.info("STEP 1/4 fetch_data — SKIPPED")

    log.info("STEP 2/4 process_indicators")
    rc = process_indicators.main()
    if rc:
        log.error("process_indicators failed with rc=%d", rc)
        return rc

    log.info("STEP 3/4 compute_index")
    rc = compute_index.main()
    if rc:
        log.error("compute_index failed with rc=%d", rc)
        return rc

    log.info("STEP 4/4 render_site")
    rc = render_site.main()
    if rc:
        log.error("render_site failed with rc=%d", rc)
        return rc

    log.info("pipeline complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
