"""Simple run metadata and watermark handling."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from retaildq.config import RetailDQConfig
from retaildq.utils.time import utc_now


def _watermark_path(config: RetailDQConfig) -> Path:
    return config.lakehouse_paths().metadata_dir / "watermarks.json"


def read_watermarks(config: RetailDQConfig) -> dict[str, Any]:
    path = _watermark_path(config)
    if not path.exists():
        return {}
    loaded: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return {str(key): value for key, value in loaded.items()}


def write_watermark(config: RetailDQConfig, run_id: str, payload: dict[str, Any]) -> None:
    paths = config.lakehouse_paths()
    paths.ensure()
    watermarks = read_watermarks(config)
    watermarks["last_run_id"] = run_id
    watermarks["updated_at"] = utc_now().isoformat()
    watermarks.setdefault("runs", {})[run_id] = payload
    _watermark_path(config).write_text(
        json.dumps(watermarks, indent=2, default=str), encoding="utf-8"
    )


def latest_run_id(config: RetailDQConfig) -> str | None:
    value = read_watermarks(config).get("last_run_id")
    return str(value) if value else None
