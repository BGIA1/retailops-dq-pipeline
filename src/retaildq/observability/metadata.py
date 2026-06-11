"""Run metadata artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from retaildq.config import RetailDQConfig
from retaildq.utils.time import utc_now


def write_run_metadata(
    config: RetailDQConfig,
    *,
    run_id: str,
    status: str,
    payload: dict[str, Any],
) -> Path:
    paths = config.lakehouse_paths()
    paths.ensure()
    metadata = {
        "run_id": run_id,
        "status": status,
        "environment": config.project.environment,
        "written_at": utc_now().isoformat(),
        **payload,
    }
    path = paths.run_layer_dir("gold", run_id) / "pipeline_run_metadata.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")

    log_path = paths.metadata_dir / "runs.jsonl"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(metadata, default=str) + "\n")
    return path
