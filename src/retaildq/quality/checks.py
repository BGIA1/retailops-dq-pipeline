"""Data quality checks derived from contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

import polars as pl

from retaildq.config import QualitySettings
from retaildq.contracts.loader import EntityContract
from retaildq.quality.quarantine import DQViolation, violation_from_row
from retaildq.utils.time import utc_today


@dataclass(frozen=True)
class CheckSummary:
    run_id: str
    entity: str
    rule_id: str
    rule_name: str
    severity: str
    status: str
    failed_records: int
    total_records: int
    details: str


def _row_dicts(frame: pl.DataFrame) -> list[dict[str, Any]]:
    return frame.to_dicts()


def _record_id(row: dict[str, Any], pk: str) -> str | None:
    value = row.get(pk)
    return None if value is None else str(value)


def _violations_from_filter(
    *,
    run_id: str,
    entity: str,
    frame: pl.DataFrame,
    mask: pl.Series,
    contract: EntityContract,
    rule_id: str,
    rule_name: str,
    severity: str,
    reason: str,
) -> list[DQViolation]:
    if frame.height == 0:
        return []
    indexed = frame.with_row_index("_row_index")
    failed = indexed.filter(mask)
    violations: list[DQViolation] = []
    for row in _row_dicts(failed):
        row_index = int(row.pop("_row_index"))
        violations.append(
            violation_from_row(
                run_id=run_id,
                entity=entity,
                record_id=_record_id(row, contract.primary_key),
                row_index=row_index,
                rule_id=rule_id,
                rule_name=rule_name,
                severity=severity,
                rejection_reason=reason,
                row=row,
            )
        )
    return violations


def _summary(
    *,
    run_id: str,
    entity: str,
    rule_id: str,
    rule_name: str,
    severity: str,
    failed_records: int,
    total_records: int,
    details: str,
) -> CheckSummary:
    return CheckSummary(
        run_id=run_id,
        entity=entity,
        rule_id=rule_id,
        rule_name=rule_name,
        severity=severity,
        status="pass" if failed_records == 0 else "fail",
        failed_records=failed_records,
        total_records=total_records,
        details=details,
    )


def validate_entity(
    *,
    run_id: str,
    entity: str,
    frame: pl.DataFrame,
    contract: EntityContract,
    references: dict[str, pl.DataFrame],
    quality: QualitySettings,
) -> tuple[list[DQViolation], list[CheckSummary]]:
    """Run row-level quality checks for one entity."""
    violations: list[DQViolation] = []
    summaries: list[CheckSummary] = []
    total = frame.height

    for column_name, column in contract.columns.items():
        rule_id = f"{entity}_{column_name}_schema_present"
        missing = column_name not in frame.columns
        summaries.append(
            _summary(
                run_id=run_id,
                entity=entity,
                rule_id=rule_id,
                rule_name="schema validation",
                severity="error",
                failed_records=total if missing else 0,
                total_records=total,
                details=f"Column {column_name} must be present",
            )
        )
        if missing:
            continue

        if not column.nullable:
            mask = frame[column_name].is_null()
            rule_id = f"{entity}_{column_name}_not_null"
            rule_violations = _violations_from_filter(
                run_id=run_id,
                entity=entity,
                frame=frame,
                mask=mask,
                contract=contract,
                rule_id=rule_id,
                rule_name="null check",
                severity="error",
                reason=f"{column_name} is required",
            )
            violations.extend(rule_violations)
            summaries.append(
                _summary(
                    run_id=run_id,
                    entity=entity,
                    rule_id=rule_id,
                    rule_name="null check",
                    severity="error",
                    failed_records=len(rule_violations),
                    total_records=total,
                    details=f"{column_name} must not be null",
                )
            )

        if column.accepted_values:
            allowed = column.accepted_values
            mask = frame[column_name].is_not_null() & frame[column_name].is_in(allowed).not_()
            rule_id = f"{entity}_{column_name}_accepted_values"
            rule_violations = _violations_from_filter(
                run_id=run_id,
                entity=entity,
                frame=frame,
                mask=mask,
                contract=contract,
                rule_id=rule_id,
                rule_name="accepted values",
                severity="error",
                reason=f"{column_name} must be one of {allowed}",
            )
            violations.extend(rule_violations)
            summaries.append(
                _summary(
                    run_id=run_id,
                    entity=entity,
                    rule_id=rule_id,
                    rule_name="accepted values",
                    severity="error",
                    failed_records=len(rule_violations),
                    total_records=total,
                    details=f"{column_name} accepted values: {', '.join(allowed)}",
                )
            )

        if column.minimum is not None:
            mask = frame[column_name].is_not_null() & (frame[column_name] < column.minimum)
            rule_id = f"{entity}_{column_name}_min_value"
            rule_violations = _violations_from_filter(
                run_id=run_id,
                entity=entity,
                frame=frame,
                mask=mask,
                contract=contract,
                rule_id=rule_id,
                rule_name="numeric range",
                severity="error",
                reason=f"{column_name} must be >= {column.minimum}",
            )
            violations.extend(rule_violations)
            summaries.append(
                _summary(
                    run_id=run_id,
                    entity=entity,
                    rule_id=rule_id,
                    rule_name="numeric range",
                    severity="error",
                    failed_records=len(rule_violations),
                    total_records=total,
                    details=f"{column_name} minimum: {column.minimum}",
                )
            )

        if column.maximum is not None:
            mask = frame[column_name].is_not_null() & (frame[column_name] > column.maximum)
            rule_id = f"{entity}_{column_name}_max_value"
            rule_violations = _violations_from_filter(
                run_id=run_id,
                entity=entity,
                frame=frame,
                mask=mask,
                contract=contract,
                rule_id=rule_id,
                rule_name="numeric range",
                severity="error",
                reason=f"{column_name} must be <= {column.maximum}",
            )
            violations.extend(rule_violations)
            summaries.append(
                _summary(
                    run_id=run_id,
                    entity=entity,
                    rule_id=rule_id,
                    rule_name="numeric range",
                    severity="error",
                    failed_records=len(rule_violations),
                    total_records=total,
                    details=f"{column_name} maximum: {column.maximum}",
                )
            )

    pk = contract.primary_key
    if pk in frame.columns:
        mask = frame[pk].is_not_null() & frame[pk].is_duplicated()
        rule_id = f"{entity}_{pk}_unique"
        rule_violations = _violations_from_filter(
            run_id=run_id,
            entity=entity,
            frame=frame,
            mask=mask,
            contract=contract,
            rule_id=rule_id,
            rule_name="primary key uniqueness",
            severity="error",
            reason=f"{pk} must be unique",
        )
        violations.extend(rule_violations)
        summaries.append(
            _summary(
                run_id=run_id,
                entity=entity,
                rule_id=rule_id,
                rule_name="primary key uniqueness",
                severity="error",
                failed_records=len(rule_violations),
                total_records=total,
                details=f"{pk} duplicates are not allowed",
            )
        )

    today = utc_today()
    end_of_today = datetime.combine(today, time.max)
    for column_name, column in contract.columns.items():
        if column.type not in {"date", "datetime"} or column_name not in frame.columns:
            continue
        comparison_value: date | datetime = end_of_today if column.type == "datetime" else today
        mask = frame[column_name].is_not_null() & (frame[column_name] > comparison_value)
        rule_id = f"{entity}_{column_name}_not_future"
        rule_violations = _violations_from_filter(
            run_id=run_id,
            entity=entity,
            frame=frame,
            mask=mask,
            contract=contract,
            rule_id=rule_id,
            rule_name="future date check",
            severity="error",
            reason=f"{column_name} must not be in the future",
        )
        violations.extend(rule_violations)
        summaries.append(
            _summary(
                run_id=run_id,
                entity=entity,
                rule_id=rule_id,
                rule_name="future date check",
                severity="error",
                failed_records=len(rule_violations),
                total_records=total,
                details=f"{column_name} must be <= {today.isoformat()}",
            )
        )

    for fk in contract.foreign_keys:
        if fk.column not in frame.columns:
            continue
        reference = references.get(fk.reference_entity)
        if reference is None or fk.reference_column not in reference.columns:
            continue
        allowed_values = reference[fk.reference_column].drop_nulls().unique().to_list()
        mask = frame[fk.column].is_not_null() & frame[fk.column].is_in(allowed_values).not_()
        rule_id = f"{entity}_{fk.column}_fk"
        rule_violations = _violations_from_filter(
            run_id=run_id,
            entity=entity,
            frame=frame,
            mask=mask,
            contract=contract,
            rule_id=rule_id,
            rule_name="referential integrity",
            severity="error",
            reason=f"{fk.column} must exist in {fk.reference_entity}.{fk.reference_column}",
        )
        violations.extend(rule_violations)
        summaries.append(
            _summary(
                run_id=run_id,
                entity=entity,
                rule_id=rule_id,
                rule_name="referential integrity",
                severity="error",
                failed_records=len(rule_violations),
                total_records=total,
                details=f"{fk.column} references {fk.reference_entity}.{fk.reference_column}",
            )
        )

    if entity == "orders" and "order_date" in frame.columns and frame.height:
        max_date = frame["order_date"].drop_nulls().max()
        stale = False
        if isinstance(max_date, date):
            stale = max_date < today - timedelta(days=quality.freshness_max_days)
        summaries.append(
            _summary(
                run_id=run_id,
                entity=entity,
                rule_id="orders_order_date_freshness",
                rule_name="freshness check",
                severity="warning",
                failed_records=1 if stale else 0,
                total_records=1,
                details=f"Latest order_date should be within {quality.freshness_max_days} days",
            )
        )

    return violations, summaries


def invalid_indices_by_entity(violations: list[DQViolation]) -> dict[str, set[int]]:
    invalid: dict[str, set[int]] = {}
    for violation in violations:
        if violation.severity != "error" or violation.row_index is None:
            continue
        invalid.setdefault(violation.entity, set()).add(violation.row_index)
    return invalid


def filter_valid_rows(frame: pl.DataFrame, invalid_indices: set[int]) -> pl.DataFrame:
    if not invalid_indices or frame.height == 0:
        return frame
    return (
        frame.with_row_index("_row_index")
        .filter(pl.col("_row_index").is_in(list(invalid_indices)).not_())
        .drop("_row_index")
    )


def summaries_to_frame(summaries: list[CheckSummary]) -> pl.DataFrame:
    rows = [summary.__dict__ for summary in summaries]
    if not rows:
        return pl.DataFrame(
            schema={
                "run_id": pl.String,
                "entity": pl.String,
                "rule_id": pl.String,
                "rule_name": pl.String,
                "severity": pl.String,
                "status": pl.String,
                "failed_records": pl.Int64,
                "total_records": pl.Int64,
                "details": pl.String,
            }
        )
    return pl.DataFrame(rows)


def invalid_rate(total_records: int, invalid_records: int) -> float:
    return 0.0 if total_records == 0 else invalid_records / total_records


def quality_gate_status(
    *, total_records: int, invalid_records: int, quality: QualitySettings
) -> tuple[bool, float]:
    rate = invalid_rate(total_records, invalid_records)
    return rate <= quality.max_invalid_rate, rate


def detect_revenue_anomalies(
    revenue_by_day: pl.DataFrame, zscore_threshold: float
) -> list[dict[str, Any]]:
    """Detect simple high-side revenue spikes using population z-score."""
    if revenue_by_day.height < 3 or "revenue" not in revenue_by_day.columns:
        return []
    revenue = revenue_by_day["revenue"].cast(pl.Float64)
    mean_raw = revenue.mean()
    std_raw = revenue.std()
    mean_value = float(mean_raw) if isinstance(mean_raw, int | float) else 0.0
    std_value = float(std_raw) if isinstance(std_raw, int | float) else 0.0
    if std_value == 0.0:
        return []
    anomalies = revenue_by_day.with_columns(
        ((pl.col("revenue") - mean_value) / std_value).alias("zscore")
    ).filter(pl.col("zscore") > zscore_threshold)
    return anomalies.to_dicts()
