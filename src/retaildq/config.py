"""Configuration loading for RetailDQ."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

from retaildq.paths import LakehousePaths


class ProjectSettings(BaseModel):
    name: str = "retaildq-lakehouse"
    environment: str = "local"


class PathSettings(BaseModel):
    data_dir: Path = Path("data")
    site_dir: Path = Path("site/generated")
    examples_dir: Path = Path("examples/demo")
    warehouse_path: Path = Path("data/retaildq.duckdb")


class GeneratorSettings(BaseModel):
    seed: int = 42
    days: int = Field(default=14, ge=1)
    orders: int = Field(default=500, ge=1)
    invalid_rate: float = Field(default=0.08, ge=0.0, le=1.0)
    customers: int = Field(default=140, ge=1)
    products: int = Field(default=80, ge=1)
    stores: int = Field(default=8, ge=1)


class QualitySettings(BaseModel):
    max_invalid_rate: float = Field(default=0.12, ge=0.0, le=1.0)
    fail_on_error: bool = True
    freshness_max_days: int = Field(default=3, ge=0)
    anomaly_revenue_zscore: float = Field(default=4.0, ge=1.0)


class DemoSettings(BaseModel):
    run_id_prefix: str = "demo"
    clean_demo_outputs: bool = True
    site_title: str = "RetailDQ Lakehouse Pipeline Demo"


class AzureSettings(BaseModel):
    storage_account_url: str | None = None
    filesystem_raw: str = "raw"
    filesystem_silver: str = "silver"
    filesystem_gold: str = "gold"
    filesystem_quarantine: str = "quarantine"
    filesystem_reports: str = "reports"
    auth_mode: str = "managed_identity_or_workload_identity"


class RetailDQConfig(BaseModel):
    project: ProjectSettings = ProjectSettings()
    paths: PathSettings = PathSettings()
    generator: GeneratorSettings = GeneratorSettings()
    quality: QualitySettings = QualitySettings()
    demo: DemoSettings = DemoSettings()
    azure: AzureSettings = AzureSettings()
    config_path: Path | None = None

    @field_validator("config_path")
    @classmethod
    def resolve_config_path(cls, value: Path | None) -> Path | None:
        return value.resolve() if value is not None else None

    def lakehouse_paths(self) -> LakehousePaths:
        return LakehousePaths(
            data_dir=self.paths.data_dir,
            site_dir=self.paths.site_dir,
            examples_dir=self.paths.examples_dir,
            warehouse_path=self.paths.warehouse_path,
        )


def _base_dir_for(config_path: Path) -> Path:
    parent = config_path.resolve().parent
    if parent.name == "configs":
        return parent.parent
    return parent


def _resolve_path(value: Path, base_dir: Path) -> Path:
    if value.is_absolute():
        return value
    return (base_dir / value).resolve()


def load_config(config_path: str | Path) -> RetailDQConfig:
    """Load YAML config and resolve local filesystem paths."""
    load_dotenv()
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw: dict[str, Any] = yaml.safe_load(handle) or {}

    raw["config_path"] = path
    config = RetailDQConfig.model_validate(raw)
    base_dir = _base_dir_for(path)
    config.paths.data_dir = _resolve_path(config.paths.data_dir, base_dir)
    config.paths.site_dir = _resolve_path(config.paths.site_dir, base_dir)
    config.paths.examples_dir = _resolve_path(config.paths.examples_dir, base_dir)
    config.paths.warehouse_path = _resolve_path(config.paths.warehouse_path, base_dir)
    return config
