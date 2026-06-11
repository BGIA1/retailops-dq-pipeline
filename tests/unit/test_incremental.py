from __future__ import annotations

from pathlib import Path

from retaildq.config import load_config
from retaildq.lakehouse.incremental import latest_run_id, read_watermarks, write_watermark


def test_incremental_watermark_roundtrip(temp_config_path: Path) -> None:
    config = load_config(temp_config_path)

    write_watermark(config, "run-1", {"status": "pass"})

    assert latest_run_id(config) == "run-1"
    assert read_watermarks(config)["runs"]["run-1"]["status"] == "pass"
