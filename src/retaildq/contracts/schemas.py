"""Schema helpers derived from data contracts."""

from __future__ import annotations

from typing import Any

import polars as pl

from retaildq.contracts.loader import EntityContract

TYPE_TO_POLARS: dict[str, Any] = {
    "string": pl.String,
    "integer": pl.Int64,
    "float": pl.Float64,
    "boolean": pl.Boolean,
    "date": pl.Date,
    "datetime": pl.Datetime,
}


def expected_polars_schema(contract: EntityContract) -> dict[str, Any]:
    return {
        name: TYPE_TO_POLARS[column.type]
        for name, column in contract.columns.items()
        if column.type in TYPE_TO_POLARS
    }


def coerce_to_contract_types(frame: pl.DataFrame, contract: EntityContract) -> pl.DataFrame:
    expressions: list[pl.Expr] = []
    for column_name, dtype in expected_polars_schema(contract).items():
        if column_name in frame.columns:
            expressions.append(pl.col(column_name).cast(dtype, strict=False).alias(column_name))
    if "run_id" in frame.columns:
        expressions.append(pl.col("run_id").cast(pl.String, strict=False).alias("run_id"))
    return frame.with_columns(expressions) if expressions else frame


def try_build_pandera_schema(contract: EntityContract) -> Any | None:
    """Build a Pandera Polars schema when the installed Pandera API supports it.

    RetailDQ uses custom row-level quality checks for quarantine traceability. This helper keeps
    Pandera wired to the data contracts without making the pipeline brittle across minor releases.
    """
    try:
        import pandera.polars as pa
    except Exception:
        return None

    dtype_map: dict[str, Any] = {
        "string": getattr(pa, "String", str),
        "integer": getattr(pa, "Int64", int),
        "float": getattr(pa, "Float64", float),
        "boolean": getattr(pa, "Bool", bool),
        "date": getattr(pa, "Date", object),
        "datetime": getattr(pa, "DateTime", object),
    }
    try:
        return pa.DataFrameSchema(
            {
                column.name: pa.Column(dtype_map.get(column.type, object), nullable=column.nullable)
                for column in contract.columns.values()
            }
        )
    except Exception:
        return None
