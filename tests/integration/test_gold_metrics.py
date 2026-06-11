from __future__ import annotations

from pathlib import Path

from retaildq.config import load_config
from retaildq.lakehouse.pipeline import run_pipeline


def test_gold_metrics_include_required_outputs(temp_config_path: Path) -> None:
    config = load_config(temp_config_path)

    result = run_pipeline(
        config=config,
        run_id="gold-run",
        seed=9,
        generate_raw=True,
        fail_on_quality_threshold=True,
    )

    assert {
        "revenue_by_day",
        "revenue_by_channel",
        "revenue_by_store",
        "order_count_by_day",
        "average_order_value",
        "top_products_by_revenue",
        "top_products_by_quantity",
        "invalid_record_counts",
        "data_quality_pass_fail_summary",
        "pipeline_run_metadata",
    }.issubset(result.gold.metrics)
