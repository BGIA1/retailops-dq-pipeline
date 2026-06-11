from __future__ import annotations

from pathlib import Path

import polars as pl

from retaildq.config import load_config
from retaildq.lakehouse.pipeline import run_pipeline


def test_full_pipeline_run_writes_layers_and_quarantine(temp_config_path: Path) -> None:
    config = load_config(temp_config_path)

    result = run_pipeline(
        config=config,
        run_id="integration-run",
        seed=7,
        generate_raw=True,
        fail_on_quality_threshold=True,
    )

    paths = config.lakehouse_paths()
    assert paths.entity_path("raw", "integration-run", "orders").exists()
    assert paths.entity_path("silver", "integration-run", "orders").exists()
    assert paths.gold_metric_path("integration-run", "revenue_by_day").exists()
    assert result.silver.quarantine.height > 0
    assert pl.read_parquet(paths.gold_metric_path("integration-run", "revenue_by_day")).height > 0
