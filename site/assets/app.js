/*
 * ADRI static site controller.
 *
 * Reads assets/adri_timeseries.json (produced by scripts/render_site.py)
 * and populates:
 *   - the latest-value card
 *   - a small SVG line chart of ADRI (and equal-weight variant)
 *   - the per-domain grid for the latest reference year
 *
 * No dependencies. Pure DOM + inline SVG.
 */

(function () {
  "use strict";

  const DATA_URL = "assets/adri_timeseries.json";

  function $(id) { return document.getElementById(id); }

  function fmt(n, digits) {
    if (n === null || n === undefined || Number.isNaN(n)) return "—";
    return Number(n).toFixed(digits === undefined ? 1 : digits);
  }

  function trendText(series) {
    if (series.length < 2) return { text: "No prior year to compare.", cls: "flat" };
    const latest = series[series.length - 1];
    const prev = series[series.length - 2];
    const delta = latest.adri - prev.adri;
    if (Math.abs(delta) < 0.5) {
      return {
        text: `Roughly flat vs. ${prev.year} (${delta >= 0 ? "+" : ""}${fmt(delta)}).`,
        cls: "flat",
      };
    }
    if (delta > 0) {
      return {
        text: `Up ${fmt(delta)} points vs. ${prev.year} — a more enabling structural reading.`,
        cls: "up",
      };
    }
    return {
      text: `Down ${fmt(Math.abs(delta))} points vs. ${prev.year} — a less enabling structural reading.`,
      cls: "down",
    };
  }

  function svgLineChart(series) {
    // Fixed viewBox; CSS scales the SVG to container width.
    const W = 640, H = 320;
    const PAD = { top: 16, right: 16, bottom: 34, left: 40 };
    const iw = W - PAD.left - PAD.right;
    const ih = H - PAD.top - PAD.bottom;

    if (!series.length) {
      return `<svg viewBox="0 0 ${W} ${H}"><text x="${W/2}" y="${H/2}" text-anchor="middle" fill="#666" font-family="Georgia, serif">No data</text></svg>`;
    }

    const years = series.map(r => r.year);
    const yMin = Math.min(...years);
    const yMax = Math.max(...years);
    const xSpan = Math.max(1, yMax - yMin);

    const values = series.flatMap(r => [r.adri, r.adri_equal_weight]).filter(v => v !== null && v !== undefined);
    const vMinRaw = Math.min(...values);
    const vMaxRaw = Math.max(...values);
    // Give the axis a small margin, and clamp to 0–100 since that is the ADRI scale.
    const vMin = Math.max(0, Math.floor((vMinRaw - 5) / 5) * 5);
    const vMax = Math.min(100, Math.ceil((vMaxRaw + 5) / 5) * 5);
    const vSpan = Math.max(1, vMax - vMin);

    function xPos(y) { return PAD.left + ((y - yMin) / xSpan) * iw; }
    function yPos(v) { return PAD.top + ih - ((v - vMin) / vSpan) * ih; }

    // Gridlines every 10 points on Y
    let gridlines = "";
    for (let v = vMin; v <= vMax; v += 10) {
      const y = yPos(v);
      gridlines += `<line x1="${PAD.left}" y1="${y}" x2="${W - PAD.right}" y2="${y}" stroke="#e6e2dc" stroke-width="1"/>`;
      gridlines += `<text x="${PAD.left - 6}" y="${y + 3}" text-anchor="end" font-size="10" fill="#5e6572" font-family="Helvetica, Arial, sans-serif">${v}</text>`;
    }

    // X axis ticks: every ~5 years
    let xticks = "";
    const step = xSpan <= 6 ? 1 : xSpan <= 14 ? 2 : 5;
    const firstTick = Math.ceil(yMin / step) * step;
    for (let y = firstTick; y <= yMax; y += step) {
      const x = xPos(y);
      xticks += `<line x1="${x}" y1="${H - PAD.bottom}" x2="${x}" y2="${H - PAD.bottom + 4}" stroke="#5e6572"/>`;
      xticks += `<text x="${x}" y="${H - PAD.bottom + 16}" text-anchor="middle" font-size="10" fill="#5e6572" font-family="Helvetica, Arial, sans-serif">${y}</text>`;
    }

    function polyline(getter, color, dash) {
      const pts = series
        .filter(r => r[getter] !== null && r[getter] !== undefined)
        .map(r => `${xPos(r.year).toFixed(1)},${yPos(r[getter]).toFixed(1)}`)
        .join(" ");
      const da = dash ? ` stroke-dasharray="${dash}"` : "";
      return `<polyline fill="none" stroke="${color}" stroke-width="2"${da} points="${pts}"/>`;
    }

    function dots(getter, color) {
      return series
        .filter(r => r[getter] !== null && r[getter] !== undefined)
        .map(r => `<circle cx="${xPos(r.year).toFixed(1)}" cy="${yPos(r[getter]).toFixed(1)}" r="2.5" fill="${color}"/>`)
        .join("");
    }

    const legend = `
      <g font-family="Helvetica, Arial, sans-serif" font-size="11" fill="#1c1e21">
        <line x1="${W - PAD.right - 200}" y1="${PAD.top + 4}" x2="${W - PAD.right - 180}" y2="${PAD.top + 4}" stroke="#2d5a8a" stroke-width="2"/>
        <text x="${W - PAD.right - 175}" y="${PAD.top + 8}">Design-weighted ADRI</text>
        <line x1="${W - PAD.right - 200}" y1="${PAD.top + 22}" x2="${W - PAD.right - 180}" y2="${PAD.top + 22}" stroke="#a3452c" stroke-width="2" stroke-dasharray="4 3"/>
        <text x="${W - PAD.right - 175}" y="${PAD.top + 26}">Equal-weight variant</text>
      </g>
    `;

    return `
      <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="ADRI line chart">
        ${gridlines}
        ${xticks}
        <line x1="${PAD.left}" y1="${H - PAD.bottom}" x2="${W - PAD.right}" y2="${H - PAD.bottom}" stroke="#5e6572"/>
        <line x1="${PAD.left}" y1="${PAD.top}" x2="${PAD.left}" y2="${H - PAD.bottom}" stroke="#5e6572"/>
        ${polyline("adri_equal_weight", "#a3452c", "4 3")}
        ${polyline("adri", "#2d5a8a", "")}
        ${dots("adri_equal_weight", "#a3452c")}
        ${dots("adri", "#2d5a8a")}
        ${legend}
      </svg>
    `;
  }

  function renderDomainGrid(latest, domainWeights) {
    const grid = $("domain-grid");
    if (!latest || !latest.domain_scores) {
      grid.innerHTML = "<p class='chart-caption'>No domain scores available.</p>";
      return;
    }
    const domains = Object.keys(domainWeights);
    grid.innerHTML = domains.map(d => {
      const score = latest.domain_scores[d];
      const w = domainWeights[d];
      const scoreText = (score === undefined || score === null) ? "—" : fmt(score, 1);
      return `
        <div class="domain-card">
          <p class="domain-name">${d}</p>
          <p class="domain-score">${scoreText}</p>
          <p class="domain-weight">weight ${w.toFixed(2)}</p>
        </div>
      `;
    }).join("");
  }

  function renderFooterMeta(payload) {
    const el = $("footer-meta");
    el.textContent =
      `Methodology version ${payload.methodology_version} — generated ${payload.generated_at}. `
      + `${payload.series.length} reference year${payload.series.length === 1 ? "" : "s"}.`;
  }

  function render(payload) {
    const series = (payload.series || []).slice().sort((a, b) => a.year - b.year);

    if (!series.length) {
      $("latest-value").textContent = "—";
      $("latest-year").textContent = "No index rows available.";
      $("chart-container").innerHTML = "<p class='chart-caption'>No data.</p>";
      renderFooterMeta(payload);
      return;
    }

    const latest = series[series.length - 1];
    $("latest-value").textContent = fmt(latest.adri, 1);
    $("latest-year").textContent = `Reference year ${latest.year}`;

    const t = trendText(series);
    const trendEl = $("latest-trend");
    trendEl.textContent = t.text;
    trendEl.className = "latest-trend " + t.cls;

    $("latest-equal").textContent =
      `Equal-weight variant: ${fmt(latest.adri_equal_weight, 1)}.`;
    $("latest-confidence").textContent =
      `Confidence: ${fmt(latest.confidence, 2)} `
      + `(1.0 = every indicator fresh; lower if any indicator carried forward or missing).`;

    $("chart-container").innerHTML = svgLineChart(series);
    $("chart-caption").textContent =
      "ADRI 0–100. Solid: design-weighted composite. Dashed: equal-weight variant across active domains.";

    renderDomainGrid(latest, payload.domain_weights || {});
    renderFooterMeta(payload);
  }

  fetch(DATA_URL, { cache: "no-cache" })
    .then(r => {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(render)
    .catch(err => {
      $("latest-value").textContent = "—";
      $("latest-year").textContent = "Could not load index data.";
      $("chart-container").innerHTML =
        "<p class='chart-caption'>Data file <code>" + DATA_URL + "</code> not found. "
        + "Run <code>python scripts/run_all.py</code> to generate it.</p>";
      console.error(err);
    });
})();
