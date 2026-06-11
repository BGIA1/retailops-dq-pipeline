"""Silver layer validation, quarantine, and persistence."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from retaildq.config import RetailDQConfig
from retaildq.contracts.loader import ENTITY_ORDER, EntityContract
from retaildq.contracts.schemas import coerce_to_contract_types, try_build_pandera_schema
from retaildq.quality.checks import (
    CheckSummary,
    filter_valid_rows,
    invalid_indices_by_entity,
    quality_gate_status,
    summaries_to_frame,
    validate_entity,
)
from retaildq.quality.quarantine import DQViolation, violation_from_row, write_quarantine
from retaildq.quality.report import write_quality_reports


@dataclass(frozen=True)
class SilverResult:
    run_id: str
    frames: dict[str, pl.DataFrame]
    quarantine: pl.DataFrame
    summary: pl.DataFrame
    gate_payload: dict[str, object]


def _add_orphan_violations(
    *,
    run_id: str,
    entity: str,
    frame: pl.DataFrame,
    contract: EntityContract,
    column: str,
    valid_values: list[object],
    reference_name: str,
) -> list[DQViolation]:
    if column not in frame.columns:
        return []
    indexed = frame.with_row_index("_row_index")
    failed = indexed.filter(
        pl.col(column).is_not_null() & pl.col(column).is_in(valid_values).not_()
    )
    rows = []
    for row in failed.to_dicts():
        row_index = int(row.pop("_row_index"))
        rows.append(
            violation_from_row(
                run_id=run_id,
                entity=entity,
                record_id=str(row.get(contract.primary_key))
                if row.get(contract.primary_key)
                else None,
                row_index=row_index,
                rule_id=f"{entity}_{column}_silver_fk",
                rule_name="silver referential integrity",
                severity="error",
                rejection_reason=f"{column} did not survive validation in {reference_name}",
                row=row,
                source_layer="silver",
            )
        )
    return rows


def build_silver(
    *,
    config: RetailDQConfig,
    run_id: str,
    raw_frames: dict[str, pl.DataFrame],
    contracts: dict[str, EntityContract],
) -> SilverResult:
    paths = config.lakehouse_paths()
    paths.ensure()
    output_dir = paths.run_layer_dir("silver", run_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    coerced = {
        entity: coerce_to_contract_types(raw_frames[entity], contracts[entity])
        for entity in ENTITY_ORDER
    }
    for entity in ENTITY_ORDER:
        try_build_pandera_schema(contracts[entity])

    violations: list[DQViolation] = []
    summaries: list[CheckSummary] = []
    for entity in ENTITY_ORDER:
        entity_violations, entity_summaries = validate_entity(
            run_id=run_id,
            entity=entity,
            frame=coerced[entity],
            contract=contracts[entity],
            references=coerced,
            quality=config.quality,
        )
        violations.extend(entity_violations)
        summaries.extend(entity_summaries)

    invalid_indices = invalid_indices_by_entity(violations)
    silver_frames = {
        entity: filter_valid_rows(coerced[entity], invalid_indices.get(entity, set()))
        for entity in ENTITY_ORDER
    }

    # Enforce FKs again after invalid parent records are removed from silver.
    orphan_violations: list[DQViolation] = []
    orphan_violations.extend(
        _add_orphan_violations(
            run_id=run_id,
            entity="orders",
            frame=silver_frames["orders"],
            contract=contracts["orders"],
            column="customer_id",
            valid_values=silver_frames["customers"]["customer_id"].to_list(),
            reference_name="customers",
        )
    )
    orphan_violations.extend(
        _add_orphan_violations(
            run_id=run_id,
            entity="orders",
            frame=silver_frames["orders"],
            contract=contracts["orders"],
            column="store_id",
            valid_values=silver_frames["stores"]["store_id"].to_list(),
            reference_name="stores",
        )
    )
    orphan_violations.extend(
        _add_orphan_violations(
            run_id=run_id,
            entity="order_items",
            frame=silver_frames["order_items"],
            contract=contracts["order_items"],
            column="order_id",
            valid_values=silver_frames["orders"]["order_id"].to_list(),
            reference_name="orders",
        )
    )
    orphan_violations.extend(
        _add_orphan_violations(
            run_id=run_id,
            entity="order_items",
            frame=silver_frames["order_items"],
            contract=contracts["order_items"],
            column="product_id",
            valid_values=silver_frames["products"]["product_id"].to_list(),
            reference_name="products",
        )
    )
    if orphan_violations:
        violations.extend(orphan_violations)
        orphan_indices = invalid_indices_by_entity(orphan_violations)
        for entity, indices in orphan_indices.items():
            silver_frames[entity] = filter_valid_rows(silver_frames[entity], indices)

    for entity in ENTITY_ORDER:
        silver_frames[entity].write_parquet(paths.entity_path("silver", run_id, entity))

    quarantine_frame = write_quarantine(paths.run_layer_dir("quarantine", run_id), violations)
    summary_frame = summaries_to_frame(summaries)
    total_records = sum(frame.height for frame in coerced.values())
    invalid_records = len(
        {
            (violation.entity, violation.row_index)
            for violation in violations
            if violation.row_index is not None
        }
    )
    passed, rate = quality_gate_status(
        total_records=total_records,
        invalid_records=invalid_records,
        quality=config.quality,
    )
    gate_payload: dict[str, object] = {
        "status": "pass" if passed else "fail",
        "passed": passed,
        "invalid_rate": rate,
        "max_invalid_rate": config.quality.max_invalid_rate,
        "total_records": total_records,
        "invalid_records": invalid_records,
        "quarantine_path": str(paths.run_layer_dir("quarantine", run_id)),
    }
    write_quality_reports(
        paths.run_layer_dir("gold", run_id),
        run_id=run_id,
        summary_frame=summary_frame,
        quarantine_frame=quarantine_frame,
        gate_payload=gate_payload,
    )
    return SilverResult(
        run_id=run_id,
        frames=silver_frames,
        quarantine=quarantine_frame,
        summary=summary_frame,
        gate_payload=gate_payload,
    )


def read_silver(config: RetailDQConfig, run_id: str) -> dict[str, pl.DataFrame]:
    paths = config.lakehouse_paths()
    frames: dict[str, pl.DataFrame] = {}
    for entity in ENTITY_ORDER:
        path = paths.entity_path("silver", run_id, entity)
        if not path.exists():
            raise FileNotFoundError(f"Missing silver entity for run {run_id}: {path}")
        frames[entity] = pl.read_parquet(path)
    return frames
