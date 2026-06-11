"""Markdown and JSON reports for data quality and gold outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import polars as pl


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def frame_preview_markdown(frame: pl.DataFrame, limit: int = 10) -> str:
    if frame.height == 0:
        return "_No rows._"
    rows = frame.head(limit).to_dicts()
    columns = frame.columns
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = [
        "| " + " | ".join(str(row.get(column, "")).replace("\n", " ") for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body])


def write_markdown_report(
    path: Path,
    *,
    title: str,
    sections: dict[str, str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", ""]
    for heading, content in sections.items():
        lines.extend([f"## {heading}", "", content, ""])
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_quality_reports(
    output_dir: Path,
    *,
    run_id: str,
    summary_frame: pl.DataFrame,
    quarantine_frame: pl.DataFrame,
    gate_payload: dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_frame.write_parquet(output_dir / "data_quality_pass_fail_summary.parquet")
    summary_frame.write_csv(output_dir / "data_quality_pass_fail_summary.csv")
    quarantine_counts = (
        quarantine_frame.group_by(["entity", "rule_id", "severity"])
        .len("invalid_records")
        .sort(["entity", "rule_id"])
        if quarantine_frame.height
        else pl.DataFrame(
            schema={
                "entity": pl.String,
                "rule_id": pl.String,
                "severity": pl.String,
                "invalid_records": pl.Int64,
            }
        )
    )
    quarantine_counts.write_parquet(output_dir / "invalid_record_counts.parquet")
    quarantine_counts.write_csv(output_dir / "invalid_record_counts.csv")
    write_json(output_dir / "data_quality_report.json", {"run_id": run_id, **gate_payload})
    write_markdown_report(
        output_dir / "data_quality_report.md",
        title=f"RetailDQ Data Quality Report - {run_id}",
        sections={
            "Gate Summary": "\n".join(
                [
                    f"- Status: `{gate_payload['status']}`",
                    f"- Invalid rate: `{gate_payload['invalid_rate']:.4f}`",
                    f"- Max invalid rate: `{gate_payload['max_invalid_rate']:.4f}`",
                    f"- Total records: `{gate_payload['total_records']}`",
                    f"- Invalid records: `{gate_payload['invalid_records']}`",
                ]
            ),
            "Rule Results": frame_preview_markdown(summary_frame, limit=30),
            "Invalid Records by Rule": frame_preview_markdown(quarantine_counts, limit=30),
            "Quarantine Strategy": (
                "Invalid records are persisted with rule ids, record ids when present, original "
                "payloads, severity, rejected timestamp, and source layer. They are isolated from "
                "silver/gold processing instead of breaking the batch."
            ),
        },
    )
