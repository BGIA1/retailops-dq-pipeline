"""Filesystem layout helpers for local and cloud-mounted lakehouse paths."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

LAKEHOUSE_LAYERS = ("raw", "silver", "gold", "quarantine")


@dataclass(frozen=True)
class LakehousePaths:
    """Resolved paths used by a pipeline run."""

    data_dir: Path
    site_dir: Path
    examples_dir: Path
    warehouse_path: Path

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def silver_dir(self) -> Path:
        return self.data_dir / "silver"

    @property
    def gold_dir(self) -> Path:
        return self.data_dir / "gold"

    @property
    def quarantine_dir(self) -> Path:
        return self.data_dir / "quarantine"

    @property
    def metadata_dir(self) -> Path:
        return self.data_dir / "_metadata"

    def ensure(self) -> None:
        for path in [
            self.data_dir,
            self.raw_dir,
            self.silver_dir,
            self.gold_dir,
            self.quarantine_dir,
            self.metadata_dir,
            self.site_dir,
            self.examples_dir,
            self.warehouse_path.parent,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def run_layer_dir(self, layer: str, run_id: str) -> Path:
        if layer not in LAKEHOUSE_LAYERS:
            raise ValueError(f"Unknown lakehouse layer: {layer}")
        return self.data_dir / layer / run_id

    def entity_path(self, layer: str, run_id: str, entity: str) -> Path:
        return self.run_layer_dir(layer, run_id) / f"{entity}.parquet"

    def gold_metric_path(self, run_id: str, metric: str, extension: str = "parquet") -> Path:
        return self.run_layer_dir("gold", run_id) / f"{metric}.{extension}"

    def remove_run(self, run_id: str) -> None:
        for layer in LAKEHOUSE_LAYERS:
            target = self.run_layer_dir(layer, run_id)
            if target.exists():
                shutil.rmtree(target)

    def remove_demo_outputs(self, run_id_prefix: str) -> None:
        for layer in LAKEHOUSE_LAYERS:
            layer_dir = self.data_dir / layer
            if not layer_dir.exists():
                continue
            for child in layer_dir.iterdir():
                if child.is_dir() and child.name.startswith(run_id_prefix):
                    shutil.rmtree(child)
        if self.site_dir.exists():
            for child in self.site_dir.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
