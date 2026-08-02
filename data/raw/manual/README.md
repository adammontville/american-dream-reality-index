# Manual raw data — vintage-of-record

Files in this directory are the **vintage-of-record** for indicators whose
primary source is a PDF, an Excel file with unstable layout, or a data
service that is impractical to automate cleanly (see METHODOLOGY.md §4).

Each CSV starts with commented header lines (prefixed `#`) that record:

- The primary source URL.
- The vintage date of the values.
- Any manual transformation steps (e.g., averaging math + reading NAEP scale
  scores; taking the age-adjusted overdose rate from NCHS Data Brief 549).

**When you update a manual file:**

1. Download the new source file (PDF, XLSX, or CSV) and archive it under
   `data/raw/manual/archive/<indicator_id>/<vintage>.<ext>` if you keep the
   archive locally. The archive itself is optional; the CSV plus its
   provenance header is what the pipeline reads.
2. Update the CSV here.
3. Bump the vintage-of-record date in the CSV's `# vintage:` header.
4. Rerun `python scripts/run_all.py` and inspect the diff in
   `data/index/adri_timeseries.json`.

See METHODOLOGY.md §6 for the full versioning and revision protocol.
