"""End-to-end pipeline orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import polars as pl

from retaildq.config import RetailDQConfig
from retaildq.contracts.loader import load_contracts
from retaildq.lakehouse.gold import GoldResult, build_gold
from retaildq.lakehouse.incremental import write_watermark
from retaildq.lakehouse.raw import RawResult, read_raw, write_raw
from retaildq.lakehouse.silver import SilverResult, build_silver
from retaildq.observability.lineage import write_lineage
from retaildq.observability.metadata import write_run_metadata
from retaildq.quality.thresholds import raise_if_threshold_failed
from retaildq.warehouse.duckdb_client import register_run_tables
from retaildq.warehouse.migrations import initialize_warehouse


@dataclass(frozen=True)
class PipelineResult:
    run_id: str
    raw: RawResult
    silver: SilverResult
    gold: GoldResult


def contract_dir_for(config: RetailDQConfig) -> Path:
    if config.config_path is not None and config.config_path.parent.name == "configs":
        return config.config_path.parent.parent / "contracts"
    return Path("contracts")


def raw_exists(config: RetailDQConfig, run_id: str) -> bool:
    paths = config.lakehouse_paths()
    return all(paths.entity_path("raw", run_id, entity).exists() for entity in load_contracts())


def _read_raw_result(config: RetailDQConfig, run_id: str) -> RawResult:
    frames = read_raw(config, run_id)
    return RawResult(
        run_id=run_id,
        frames=frames,
        counts={entity: frame.height for entity, frame in frames.items()},
    )


def _payload_float(payload: dict[str, object], key: str, default: float = 0.0) -> float:
    value = payload.get(key, default)
    return float(value) if isinstance(value, int | float) else default


def run_pipeline(
    *,
    config: RetailDQConfig,
    run_id: str,
    seed: int | None = None,
    generate_raw: bool = True,
    fail_on_quality_threshold: bool = True,
) -> PipelineResult:
    """Run raw to silver to gold for a single run id."""
    paths = config.lakehouse_paths()
    paths.ensure()
    initialize_warehouse(config)
    contracts = load_contracts(contract_dir_for(config))

    if generate_raw or not all(
        paths.entity_path("raw", run_id, entity).exists() for entity in contracts
    ):
        raw = write_raw(config, run_id=run_id, seed=seed)
    else:
        raw = _read_raw_result(config, run_id)

    silver = build_silver(
        config=config,
        run_id=run_id,
        raw_frames=raw.frames,
        contracts=contracts,
    )
    gold = build_gold(
        config=config,
        run_id=run_id,
        silver_frames=silver.frames,
        quarantine_frame=silver.quarantine,
        gate_payload=silver.gate_payload,
        raw_counts=raw.counts,
    )
    write_lineage(paths.run_layer_dir("gold", run_id), run_id)
    register_run_tables(config, run_id)
    write_run_metadata(
        config,
        run_id=run_id,
        status=str(silver.gate_payload["status"]),
        payload={
            "raw_counts": raw.counts,
            "silver_counts": {entity: frame.height for entity, frame in silver.frames.items()},
            "quality": silver.gate_payload,
            "gold_metrics": list(gold.metrics),
            "anomaly_count": len(gold.anomalies),
        },
    )
    write_watermark(
        config,
        run_id,
        {
            "status": silver.gate_payload["status"],
            "invalid_rate": silver.gate_payload["invalid_rate"],
            "raw_records": sum(raw.counts.values()),
            "silver_records": sum(frame.height for frame in silver.frames.values()),
        },
    )

    if fail_on_quality_threshold:
        raise_if_threshold_failed(
            bool(silver.gate_payload["passed"]),
            _payload_float(silver.gate_payload, "invalid_rate"),
            config.quality.max_invalid_rate,
        )

    return PipelineResult(run_id=run_id, raw=raw, silver=silver, gold=gold)


def read_gold_metric(config: RetailDQConfig, run_id: str, metric: str) -> pl.DataFrame:
    path = config.lakehouse_paths().gold_metric_path(run_id, metric)
    if not path.exists():
        raise FileNotFoundError(f"Gold metric not found: {path}")
    return pl.read_parquet(path)
