"""Raw layer generation and persistence."""

from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from retaildq.config import RetailDQConfig
from retaildq.contracts.loader import ENTITY_ORDER
from retaildq.generator.synthetic_retail import (
    SyntheticRetailConfig,
    generate_synthetic_retail_data,
)


@dataclass(frozen=True)
class RawResult:
    run_id: str
    frames: dict[str, pl.DataFrame]
    counts: dict[str, int]


def _generator_config(config: RetailDQConfig, seed: int | None = None) -> SyntheticRetailConfig:
    settings = config.generator
    return SyntheticRetailConfig(
        seed=settings.seed if seed is None else seed,
        days=settings.days,
        orders=settings.orders,
        invalid_rate=settings.invalid_rate,
        customers=settings.customers,
        products=settings.products,
        stores=settings.stores,
    )


def write_raw(config: RetailDQConfig, run_id: str, seed: int | None = None) -> RawResult:
    paths = config.lakehouse_paths()
    paths.ensure()
    output_dir = paths.run_layer_dir("raw", run_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = generate_synthetic_retail_data(_generator_config(config, seed=seed))
    frames_with_run = {
        entity: frame.with_columns(pl.lit(run_id).alias("run_id"))
        for entity, frame in frames.items()
    }
    for entity in ENTITY_ORDER:
        frames_with_run[entity].write_parquet(paths.entity_path("raw", run_id, entity))
    return RawResult(
        run_id=run_id,
        frames=frames_with_run,
        counts={entity: frames_with_run[entity].height for entity in ENTITY_ORDER},
    )


def read_raw(config: RetailDQConfig, run_id: str) -> dict[str, pl.DataFrame]:
    paths = config.lakehouse_paths()
    frames: dict[str, pl.DataFrame] = {}
    for entity in ENTITY_ORDER:
        path = paths.entity_path("raw", run_id, entity)
        if not path.exists():
            raise FileNotFoundError(f"Missing raw entity for run {run_id}: {path}")
        frames[entity] = pl.read_parquet(path)
    return frames
