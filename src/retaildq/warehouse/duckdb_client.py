"""DuckDB persistence for silver and gold layers."""

from __future__ import annotations

from pathlib import Path

import duckdb

from retaildq.config import RetailDQConfig
from retaildq.contracts.loader import ENTITY_ORDER


def register_run_tables(config: RetailDQConfig, run_id: str) -> None:
    paths = config.lakehouse_paths()
    paths.warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(paths.warehouse_path)) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS silver")
        conn.execute("CREATE SCHEMA IF NOT EXISTS gold")
        for entity in ENTITY_ORDER:
            source = paths.entity_path("silver", run_id, entity).as_posix()
            conn.execute(
                f"CREATE OR REPLACE TABLE silver.{entity} AS SELECT * FROM read_parquet('{source}')"
            )
        for metric_path in paths.run_layer_dir("gold", run_id).glob("*.parquet"):
            table_name = metric_path.stem
            source = metric_path.as_posix()
            conn.execute(
                f"CREATE OR REPLACE TABLE gold.{table_name} AS "
                f"SELECT * FROM read_parquet('{source}')"
            )


def query_scalar(database_path: Path, sql: str) -> object:
    with duckdb.connect(str(database_path), read_only=True) as conn:
        row = conn.execute(sql).fetchone()
        if row is None:
            return None
        return row[0]
