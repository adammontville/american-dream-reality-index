"""
render_site.py — Copy the computed index JSON/CSV into site/assets/ and
render docs/METHODOLOGY.md into site/methodology.html.

The site itself (site/index.html) is a static file that reads
site/assets/adri_timeseries.json. This script only needs to keep the
assets and methodology page in sync with the source.

Markdown-to-HTML is done with a tiny built-in converter that handles the
subset of Markdown used in METHODOLOGY.md (headings, tables, code blocks,
inline code, links, bold/italic, math delimiters passed through). Using
a hand-rolled converter avoids adding a Python dependency for a one-off
static export, per the "minimal dependencies" constraint in the Thread 2
prompt.
"""

from __future__ import annotations

import html
import logging
import re
import shutil
from pathlib import Path

from config import DOCS_DIR, INDEX_DIR, SITE_ASSETS_DIR, SITE_DIR, ensure_dirs

log = logging.getLogger("render_site")


# ---------------------------------------------------------------------------
# Minimal Markdown → HTML converter
# ---------------------------------------------------------------------------

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    # Restore Markdown-style tokens we escaped above so regexes can act on them.
    # (html.escape does not touch * or `.)
    s = INLINE_CODE.sub(lambda m: f"<code>{m.group(1)}</code>", s)
    s = BOLD.sub(lambda m: f"<strong>{m.group(1)}</strong>", s)
    s = LINK.sub(
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        s,
    )
    return s


def _render_table(header_line: str, sep_line: str, body_lines: list[str]) -> str:
    def cells(row: str) -> list[str]:
        r = row.strip()
        if r.startswith("|"):
            r = r[1:]
        if r.endswith("|"):
            r = r[:-1]
        return [c.strip() for c in r.split("|")]

    thead = "".join(f"<th>{_inline(c)}</th>" for c in cells(header_line))
    tbody_rows = []
    for row in body_lines:
        tbody_rows.append(
            "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells(row)) + "</tr>"
        )
    return (
        '<div class="table-wrap"><table>'
        f"<thead><tr>{thead}</tr></thead>"
        f"<tbody>{''.join(tbody_rows)}</tbody>"
        "</table></div>"
    )


def markdown_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    in_code = False
    para: list[str] = []

    def flush_para() -> None:
        if para:
            out.append(f"<p>{_inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            flush_para()
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append('<pre><code>')
                in_code = True
            i += 1
            continue
        if in_code:
            out.append(html.escape(line, quote=False))
            i += 1
            continue

        if not line.strip():
            flush_para()
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para()
            level = len(m.group(1))
            text = m.group(2)
            # Slug for anchor links: lowercase, keep alnum, dashes, and dots;
            # collapse other chars to a dash; trim leading/trailing dashes.
            slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(
                f'<h{level} id="{slug}">{_inline(text)}</h{level}>'
            )
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^-{3,}\s*$", line):
            flush_para()
            out.append("<hr/>")
            i += 1
            continue

        # Tables (header | sep | body)
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$", lines[i + 1]
        ):
            flush_para()
            header = line
            sep = lines[i + 1]
            body: list[str] = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                body.append(lines[j])
                j += 1
            out.append(_render_table(header, sep, body))
            i = j
            continue

        # Unordered list
        if re.match(r"^\s*[-*]\s+", line):
            flush_para()
            items: list[str] = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            out.append(
                "<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ul>"
            )
            continue

        # Ordered list
        if re.match(r"^\s*\d+\.\s+", line):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append(
                "<ol>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + "</ol>"
            )
            continue

        # Blockquote
        if line.startswith("> "):
            flush_para()
            out.append(f"<blockquote>{_inline(line[2:])}</blockquote>")
            i += 1
            continue

        para.append(line)
        i += 1

    flush_para()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

METHODOLOGY_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>American Dream Reality Index — Methodology</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="assets/style.css"/>
</head>
<body>
  <header class="site-header">
    <nav><a href="index.html">← ADRI</a></nav>
    <h1>Methodology</h1>
    <p class="tagline">
      Rendered from
      <code>docs/METHODOLOGY.md</code>.
      This is the authoritative description of the index.
    </p>
  </header>
  <main class="prose">
    {body}
  </main>
  <footer class="site-footer">
    <p>Generated by <code>scripts/render_site.py</code>.</p>
    <p class="footer-license">
      © 2026 Adam Montville.
      Open-source under
      <a href="https://github.com/AdamMontville/american-dream-reality-index/blob/main/LICENSE.md">AGPL-3.0</a>.
      <a href="https://github.com/AdamMontville/american-dream-reality-index/blob/main/COMMERCIAL_LICENSE.md">Commercial use</a>
      requires a separate license.
    </p>
  </footer>
</body>
</html>
"""


def render_methodology() -> None:
    src = DOCS_DIR / "METHODOLOGY.md"
    dst = SITE_DIR / "methodology.html"
    md = src.read_text(encoding="utf-8")
    body = markdown_to_html(md)
    dst.write_text(METHODOLOGY_HTML_TEMPLATE.format(body=body), encoding="utf-8")
    log.info("wrote %s", dst)


def copy_index_assets() -> None:
    for name in ("adri_timeseries.json", "adri_timeseries.csv"):
        src = INDEX_DIR / name
        if not src.exists():
            log.warning("index artifact %s missing; skip copy", src)
            continue
        dst = SITE_ASSETS_DIR / name
        shutil.copy2(src, dst)
        log.info("copied %s -> %s", src, dst)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    ensure_dirs()
    render_methodology()
    copy_index_assets()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
