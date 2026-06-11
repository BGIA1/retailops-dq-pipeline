"""Quarantine serialization for invalid records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl

from retaildq.utils.time import utc_now


@dataclass(frozen=True)
class DQViolation:
    run_id: str
    entity: str
    record_id: str | None
    row_index: int | None
    rule_id: str
    rule_name: str
    severity: str
    rejection_reason: str
    rejected_at: datetime
    original_payload: dict[str, Any]
    source_layer: str = "raw"


def payload_to_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, default=str, sort_keys=True)


def violation_from_row(
    *,
    run_id: str,
    entity: str,
    record_id: str | None,
    row_index: int | None,
    rule_id: str,
    rule_name: str,
    severity: str,
    rejection_reason: str,
    row: dict[str, Any],
    source_layer: str = "raw",
) -> DQViolation:
    return DQViolation(
        run_id=run_id,
        entity=entity,
        record_id=record_id,
        row_index=row_index,
        rule_id=rule_id,
        rule_name=rule_name,
        severity=severity,
        rejection_reason=rejection_reason,
        rejected_at=utc_now(),
        original_payload=row,
        source_layer=source_layer,
    )


def violations_to_frame(violations: list[DQViolation]) -> pl.DataFrame:
    rows = [
        {
            "run_id": item.run_id,
            "entity": item.entity,
            "record_id": item.record_id,
            "row_index": item.row_index,
            "rule_id": item.rule_id,
            "rule_name": item.rule_name,
            "severity": item.severity,
            "rejection_reason": item.rejection_reason,
            "rejected_at": item.rejected_at,
            "original_payload": payload_to_json(item.original_payload),
            "source_layer": item.source_layer,
        }
        for item in violations
    ]
    schema: dict[str, Any] = {
        "run_id": pl.String,
        "entity": pl.String,
        "record_id": pl.String,
        "row_index": pl.Int64,
        "rule_id": pl.String,
        "rule_name": pl.String,
        "severity": pl.String,
        "rejection_reason": pl.String,
        "rejected_at": pl.Datetime(time_zone="UTC"),
        "original_payload": pl.String,
        "source_layer": pl.String,
    }
    if not rows:
        return pl.DataFrame(schema=schema)
    return pl.DataFrame(rows, schema=schema, strict=False)


def write_quarantine(path: Path, violations: list[DQViolation]) -> pl.DataFrame:
    path.mkdir(parents=True, exist_ok=True)
    frame = violations_to_frame(violations)
    frame.write_parquet(path / "quarantine.parquet")
    frame.write_csv(path / "quarantine.csv")
    return frame
