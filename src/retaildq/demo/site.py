"""Static GitHub Pages demo generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import polars as pl
from jinja2 import Template

from retaildq.config import RetailDQConfig
from retaildq.quality.report import frame_preview_markdown

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }}</title>
  <style>
    :root {
      --bg: #f7f8fb;
      --ink: #17202a;
      --muted: #536475;
      --panel: #ffffff;
      --border: #d7dee8;
      --accent: #136f63;
      --warn: #8f4b00;
      --bad: #9d1c20;
    }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }
    header {
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      padding: 32px max(24px, calc((100vw - 1120px) / 2));
    }
    main {
      max-width: 1120px;
      margin: 0 auto;
      padding: 24px;
    }
    h1, h2, h3 { margin: 0 0 12px; }
    h1 { font-size: 32px; }
    h2 { font-size: 22px; margin-top: 28px; }
    p { color: var(--muted); }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }
    .metric {
      font-size: 28px;
      font-weight: 700;
      color: var(--accent);
    }
    .fail { color: var(--bad); }
    .warn { color: var(--warn); }
    table {
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      display: block;
      overflow-x: auto;
      white-space: nowrap;
    }
    th, td {
      padding: 8px 10px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      font-size: 13px;
    }
    code {
      background: #eef2f6;
      padding: 2px 5px;
      border-radius: 4px;
    }
    pre {
      background: #0f1720;
      color: #e6edf3;
      padding: 16px;
      border-radius: 8px;
      overflow-x: auto;
    }
  </style>
</head>
<body>
  <header>
    <h1>{{ title }}</h1>
    <p>Local-first retail lakehouse pipeline demo: synthetic raw data, data contracts, quality gates, quarantine, silver/gold marts, and Azure deployment readiness.</p>
  </header>
  <main>
    <section class="grid">
      <div class="card"><h3>Run ID</h3><div class="metric">{{ run_id }}</div></div>
      <div class="card"><h3>DQ Status</h3><div class="metric {{ 'fail' if dq.status == 'fail' else '' }}">{{ dq.status }}</div></div>
      <div class="card"><h3>Invalid Rate</h3><div class="metric">{{ "%.2f"|format(dq.invalid_rate * 100) }}%</div></div>
      <div class="card"><h3>Invalid Records</h3><div class="metric">{{ dq.invalid_records }}</div></div>
    </section>

    <section>
      <h2>Pipeline Architecture</h2>
      <pre>Generator -> Raw -> Contracts + DQ -> Quarantine + Silver -> Gold -> Reports/Site</pre>
    </section>

    <section>
      <h2>Executive Summary</h2>
      <p>This demo is intentionally pipeline-first. It shows how bad records are isolated with traceability while valid data continues into typed silver tables and analytical gold outputs.</p>
    </section>

    <section>
      <h2>Run Metadata</h2>
      {{ metadata_table }}
    </section>

    <section>
      <h2>Data Quality Summary</h2>
      {{ dq_table }}
    </section>

    <section>
      <h2>Invalid Records Summary</h2>
      {{ invalid_table }}
    </section>

    <section>
      <h2>Gold Metrics</h2>
      <h3>Revenue by Day</h3>
      {{ revenue_by_day }}
      <h3>Revenue by Channel</h3>
      {{ revenue_by_channel }}
      <h3>Top Products by Revenue</h3>
      {{ top_products }}
    </section>

    <section>
      <h2>Lineage Summary</h2>
      <p>Raw entities flow into validated silver tables. Gold marts join silver order headers, order items, stores, products, and quarantine summaries.</p>
    </section>

    <section>
      <h2>Limitations</h2>
      <p>Synthetic batch data only; no real PII, no real-time streaming, no live Azure resources, and no interactive dashboard in V1.</p>
    </section>

    <section>
      <h2>Cost Statement</h2>
      <p>Local execution costs $0 MXN. GitHub Pages/Actions are expected to be $0 within normal included GitHub usage. Azure costs begin only after a future manual deployment.</p>
    </section>
  </main>
</body>
</html>
"""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    loaded: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return {str(key): value for key, value in loaded.items()}


def _read_metric(config: RetailDQConfig, run_id: str, metric: str) -> pl.DataFrame:
    path = config.lakehouse_paths().gold_metric_path(run_id, metric)
    if not path.exists():
        return pl.DataFrame()
    return pl.read_parquet(path)


def _markdown_to_html_table(markdown: str) -> str:
    if markdown == "_No rows._":
        return "<p><em>No rows.</em></p>"
    lines = [line for line in markdown.splitlines() if line.startswith("|")]
    if len(lines) < 2:
        return f"<pre>{markdown}</pre>"
    headers = [value.strip() for value in lines[0].strip("|").split("|")]
    body_lines = lines[2:]
    html = ["<table><thead><tr>"]
    html.extend(f"<th>{header}</th>" for header in headers)
    html.append("</tr></thead><tbody>")
    for line in body_lines:
        values = [value.strip() for value in line.strip("|").split("|")]
        html.append("<tr>")
        html.extend(f"<td>{value}</td>" for value in values)
        html.append("</tr>")
    html.append("</tbody></table>")
    return "".join(html)


def _frame_to_html(frame: pl.DataFrame, limit: int = 10) -> str:
    return _markdown_to_html_table(frame_preview_markdown(frame, limit=limit))


def build_static_site(config: RetailDQConfig, run_id: str) -> Path:
    paths = config.lakehouse_paths()
    output_dir = paths.site_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    gold_dir = paths.run_layer_dir("gold", run_id)
    dq_payload = _read_json(gold_dir / "data_quality_report.json")
    dq = {
        "status": dq_payload.get("status", "unknown"),
        "invalid_rate": float(dq_payload.get("invalid_rate", 0.0)),
        "invalid_records": int(dq_payload.get("invalid_records", 0)),
    }

    html = Template(HTML_TEMPLATE).render(
        title=config.demo.site_title,
        run_id=run_id,
        dq=dq,
        metadata_table=_frame_to_html(_read_metric(config, run_id, "pipeline_run_metadata")),
        dq_table=_frame_to_html(_read_metric(config, run_id, "data_quality_pass_fail_summary")),
        invalid_table=_frame_to_html(
            _read_metric(config, run_id, "invalid_record_counts"), limit=20
        ),
        revenue_by_day=_frame_to_html(_read_metric(config, run_id, "revenue_by_day"), limit=14),
        revenue_by_channel=_frame_to_html(_read_metric(config, run_id, "revenue_by_channel")),
        top_products=_frame_to_html(_read_metric(config, run_id, "top_products_by_revenue")),
    )
    index_path = output_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")

    readme = "\n".join(
        [
            f"# {config.demo.site_title}",
            "",
            f"- Run ID: `{run_id}`",
            f"- DQ status: `{dq['status']}`",
            f"- Invalid rate: `{dq['invalid_rate']:.4f}`",
            "- This folder is generated from synthetic local outputs and is safe for GitHub Pages.",
            "",
        ]
    )
    (output_dir / "README.md").write_text(readme, encoding="utf-8")
    return index_path
