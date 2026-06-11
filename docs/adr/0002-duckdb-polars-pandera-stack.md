# ADR 0002: DuckDB, Polars, and Pandera Stack

## Status

Accepted

## Decision

Use Polars for local DataFrame processing, DuckDB for lightweight warehouse registration, Pandera as a schema companion, and custom checks for row-level quarantine traceability.

## Consequences

The stack stays lightweight and batch-friendly without introducing Spark, dbt, or heavy services in V1.
