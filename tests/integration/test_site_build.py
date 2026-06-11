from __future__ import annotations

from pathlib import Path

from retaildq.config import load_config
from retaildq.demo.site import build_static_site
from retaildq.lakehouse.pipeline import run_pipeline


def test_site_build_generates_index(temp_config_path: Path) -> None:
    config = load_config(temp_config_path)
    run_pipeline(
        config=config,
        run_id="site-run",
        seed=11,
        generate_raw=True,
        fail_on_quality_threshold=True,
    )

    index = build_static_site(config, "site-run")

    assert index.exists()
    assert "RetailDQ Pytest Demo" in index.read_text(encoding="utf-8")
