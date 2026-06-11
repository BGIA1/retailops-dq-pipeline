"""Minimal local DuckDB migration helpers."""

from __future__ import annotations

import duckdb

from retaildq.config import RetailDQConfig


def initialize_warehouse(config: RetailDQConfig) -> None:
    paths = config.lakehouse_paths()
    paths.warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(paths.warehouse_path)) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS silver")
        conn.execute("CREATE SCHEMA IF NOT EXISTS gold")
        conn.execute("CREATE SCHEMA IF NOT EXISTS observability")
