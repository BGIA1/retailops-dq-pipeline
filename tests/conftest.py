from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    shutil.copytree(REPO_ROOT / "contracts", project / "contracts")
    (project / "configs").mkdir()
    return project


@pytest.fixture
def temp_config_path(temp_project: Path) -> Path:
    config: dict[str, Any] = {
        "project": {"name": "retaildq-test", "environment": "test"},
        "paths": {
            "data_dir": "data",
            "site_dir": "site/generated",
            "examples_dir": "examples/demo",
            "warehouse_path": "data/retaildq.duckdb",
        },
        "generator": {
            "seed": 7,
            "days": 5,
            "orders": 40,
            "invalid_rate": 0.10,
            "customers": 20,
            "products": 12,
            "stores": 3,
        },
        "quality": {
            "max_invalid_rate": 0.50,
            "fail_on_error": True,
            "freshness_max_days": 3,
            "anomaly_revenue_zscore": 3.0,
        },
        "demo": {
            "run_id_prefix": "pytest-demo",
            "clean_demo_outputs": True,
            "site_title": "RetailDQ Pytest Demo",
        },
    }
    path = temp_project / "configs" / "test.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return path
