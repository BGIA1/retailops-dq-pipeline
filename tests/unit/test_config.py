from __future__ import annotations

from pathlib import Path

from retaildq.config import load_config


def test_config_paths_resolve_against_project_root(temp_config_path: Path) -> None:
    config = load_config(temp_config_path)

    assert config.project.environment == "test"
    assert config.paths.data_dir == temp_config_path.parent.parent / "data"
    assert config.paths.warehouse_path.name == "retaildq.duckdb"
