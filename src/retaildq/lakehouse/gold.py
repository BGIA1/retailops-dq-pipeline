"""Gold mart generation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl

from retaildq.config import RetailDQConfig
from retaildq.quality.checks import detect_revenue_anomalies
from retaildq.quality.report import frame_preview_markdown, write_markdown_report

REVENUE_STATUSES = ["paid", "shipped"]


@dataclass(frozen=True)
class GoldResult:
    run_id: str
    metrics: dict[str, pl.DataFrame]
    anomalies: list[dict[str, Any]]


def _payload_int(payload: dict[str, object], key: str, default: int = 0) -> int:
    value = payload.get(key, default)
    return value if isinstance(value, int) else default


def _payload_str(payload: dict[str, object], key: str, default: str = "") -> str:
    value = payload.get(key, default)
    return value if isinstance(value, str) else default


def _write_metric(output_dir: Path, name: str, frame: pl.DataFrame) -> None:
    frame.write_parquet(output_dir / f"{name}.parquet")
    frame.write_csv(output_dir / f"{name}.csv")


def _line_items(silver_frames: dict[str, pl.DataFrame]) -> pl.DataFrame:
    orders = silver_frames["orders"]
    items = silver_frames["order_items"]
    products = silver_frames["products"].select(["product_id", "category"])
    stores = silver_frames["stores"].select(["store_id", "region"])
    return (
        items.join(orders, on="order_id", how="inner")
        .join(products, on="product_id", how="left")
        .join(stores, on="store_id", how="left")
        .with_columns((pl.col("quantity") * pl.col("unit_price")).alias("line_revenue"))
    )


def build_gold(
    *,
    config: RetailDQConfig,
    run_id: str,
    silver_frames: dict[str, pl.DataFrame],
    quarantine_frame: pl.DataFrame,
    gate_payload: dict[str, object],
    raw_counts: dict[str, int],
) -> GoldResult:
    paths = config.lakehouse_paths()
    output_dir = paths.run_layer_dir("gold", run_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    line_items = _line_items(silver_frames)
    revenue_items = line_items.filter(pl.col("order_status").is_in(REVENUE_STATUSES))

    revenue_by_day = (
        revenue_items.group_by("order_date")
        .agg(pl.col("line_revenue").sum().round(2).alias("revenue"))
        .sort("order_date")
    )
    revenue_by_channel = (
        revenue_items.group_by("channel")
        .agg(pl.col("line_revenue").sum().round(2).alias("revenue"))
        .sort("revenue", descending=True)
    )
    revenue_by_store = (
        revenue_items.group_by(["store_id", "region"])
        .agg(pl.col("line_revenue").sum().round(2).alias("revenue"))
        .sort("revenue", descending=True)
    )
    order_count_by_day = (
        silver_frames["orders"].group_by("order_date").len("order_count").sort("order_date")
    )
    order_totals = (
        revenue_items.group_by("order_id")
        .agg(pl.col("line_revenue").sum().alias("order_revenue"))
        .sort("order_id")
    )
    average_order_value = pl.DataFrame(
        [
            {
                "metric": "average_order_value",
                "value": round(
                    float(mean_value)
                    if isinstance(mean_value := order_totals["order_revenue"].mean(), int | float)
                    else 0.0,
                    2,
                ),
                "order_count": order_totals.height,
            }
        ]
    )
    top_products_by_revenue = (
        revenue_items.group_by(["product_id", "category"])
        .agg(pl.col("line_revenue").sum().round(2).alias("revenue"))
        .sort("revenue", descending=True)
        .head(10)
    )
    top_products_by_quantity = (
        revenue_items.group_by(["product_id", "category"])
        .agg(pl.col("quantity").sum().alias("quantity"))
        .sort("quantity", descending=True)
        .head(10)
    )
    invalid_record_counts = (
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
    data_quality_pass_fail_summary = pl.DataFrame([gate_payload])
    pipeline_run_metadata = pl.DataFrame(
        [
            {
                "run_id": run_id,
                "environment": config.project.environment,
                "raw_records": sum(raw_counts.values()),
                "silver_records": sum(frame.height for frame in silver_frames.values()),
                "invalid_records": _payload_int(gate_payload, "invalid_records"),
                "quality_status": _payload_str(gate_payload, "status", "unknown"),
                "warehouse_path": str(paths.warehouse_path),
            }
        ]
    )

    metrics = {
        "revenue_by_day": revenue_by_day,
        "revenue_by_channel": revenue_by_channel,
        "revenue_by_store": revenue_by_store,
        "order_count_by_day": order_count_by_day,
        "average_order_value": average_order_value,
        "top_products_by_revenue": top_products_by_revenue,
        "top_products_by_quantity": top_products_by_quantity,
        "invalid_record_counts": invalid_record_counts,
        "data_quality_pass_fail_summary": data_quality_pass_fail_summary,
        "pipeline_run_metadata": pipeline_run_metadata,
    }
    for name, frame in metrics.items():
        _write_metric(output_dir, name, frame)

    anomalies = detect_revenue_anomalies(
        revenue_by_day, zscore_threshold=config.quality.anomaly_revenue_zscore
    )
    (output_dir / "anomaly_report.json").write_text(
        json.dumps({"run_id": run_id, "anomalies": anomalies}, indent=2, default=str),
        encoding="utf-8",
    )
    write_markdown_report(
        output_dir / "gold_metrics_summary.md",
        title=f"RetailDQ Gold Metrics Summary - {run_id}",
        sections={
            "Revenue by Day": frame_preview_markdown(revenue_by_day),
            "Revenue by Channel": frame_preview_markdown(revenue_by_channel),
            "Average Order Value": frame_preview_markdown(average_order_value),
            "Top Products by Revenue": frame_preview_markdown(top_products_by_revenue),
            "Data Quality Summary": frame_preview_markdown(data_quality_pass_fail_summary),
        },
    )
    return GoldResult(run_id=run_id, metrics=metrics, anomalies=anomalies)
