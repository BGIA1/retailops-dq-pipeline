"""RetailDQ command line interface."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from retaildq.config import RetailDQConfig, load_config
from retaildq.contracts.loader import load_contracts
from retaildq.demo.site import build_static_site
from retaildq.lakehouse.incremental import latest_run_id
from retaildq.lakehouse.pipeline import contract_dir_for, run_pipeline
from retaildq.lakehouse.raw import write_raw
from retaildq.logging import configure_logging
from retaildq.quality.report import write_markdown_report

app = typer.Typer(no_args_is_help=True, help="RetailDQ Lakehouse Pipeline CLI.")
console = Console()


ConfigOption = Annotated[
    Path,
    typer.Option("--config", "-c", exists=True, dir_okay=False, help="Path to YAML config."),
]
RunIdOption = Annotated[
    str | None,
    typer.Option("--run-id", help="Optional run id. Defaults to latest run or a new id."),
]


def _load(config: Path) -> RetailDQConfig:
    configure_logging()
    return load_config(config)


def _resolve_run_id(config_path: Path, run_id: str | None) -> str:
    config = load_config(config_path)
    if run_id:
        return run_id
    latest = latest_run_id(config)
    if latest:
        return latest
    return f"{config.demo.run_id_prefix}-sample"


@app.command()
def generate(
    config: ConfigOption = Path("configs/local.yaml"),
    seed: Annotated[int | None, typer.Option("--seed", help="Override generator seed.")] = None,
    days: Annotated[
        int | None, typer.Option("--days", help="Override generated day window.")
    ] = None,
    orders: Annotated[int | None, typer.Option("--orders", help="Override order count.")] = None,
    invalid_rate: Annotated[
        float | None,
        typer.Option("--invalid-rate", min=0.0, max=1.0, help="Override invalid rate."),
    ] = None,
    run_id: RunIdOption = None,
) -> None:
    """Generate raw synthetic data."""
    cfg = _load(config)
    if days is not None:
        cfg.generator.days = days
    if orders is not None:
        cfg.generator.orders = orders
    if invalid_rate is not None:
        cfg.generator.invalid_rate = invalid_rate
    final_run_id = run_id or f"{cfg.demo.run_id_prefix}-sample"
    result = write_raw(cfg, run_id=final_run_id, seed=seed)
    console.print(f"Generated raw data for [bold]{final_run_id}[/bold]: {result.counts}")


@app.command()
def run(
    config: ConfigOption = Path("configs/local.yaml"),
    run_id: RunIdOption = None,
    fail_on_quality_threshold: Annotated[
        bool,
        typer.Option(
            "--fail-on-quality-threshold/--no-fail-on-quality-threshold",
            help="Fail if invalid rate exceeds configured threshold.",
        ),
    ] = True,
) -> None:
    """Run the complete raw -> silver -> gold pipeline."""
    cfg = _load(config)
    final_run_id = run_id or f"{cfg.demo.run_id_prefix}-sample"
    result = run_pipeline(
        config=cfg,
        run_id=final_run_id,
        generate_raw=True,
        fail_on_quality_threshold=fail_on_quality_threshold,
    )
    console.print(
        f"Pipeline run [bold]{result.run_id}[/bold] complete. "
        f"DQ status: {result.silver.gate_payload['status']}"
    )


@app.command()
def validate(
    config: ConfigOption = Path("configs/local.yaml"),
    run_id: RunIdOption = None,
) -> None:
    """Validate raw data and rebuild silver/quarantine quality artifacts."""
    cfg = _load(config)
    final_run_id = _resolve_run_id(config, run_id)
    result = run_pipeline(
        config=cfg,
        run_id=final_run_id,
        generate_raw=False,
        fail_on_quality_threshold=False,
    )
    console.print(
        f"Validation complete for [bold]{result.run_id}[/bold]. "
        f"Invalid rate: {_payload_float(result.silver.gate_payload, 'invalid_rate'):.4f}"
    )


def _copy_if_exists(source: Path, destination: Path) -> None:
    if source.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def _payload_float(payload: dict[str, object], key: str, default: float = 0.0) -> float:
    value = payload.get(key, default)
    return float(value) if isinstance(value, int | float) else default


@app.command()
def report(
    config: ConfigOption = Path("configs/local.yaml"),
    run_id: RunIdOption = None,
    format: Annotated[
        str, typer.Option("--format", help="Report format: markdown, json, or all.")
    ] = "all",
) -> None:
    """Generate or copy report artifacts for a run."""
    cfg = _load(config)
    final_run_id = _resolve_run_id(config, run_id)
    paths = cfg.lakehouse_paths()
    gold_dir = paths.run_layer_dir("gold", final_run_id)
    if not gold_dir.exists():
        raise typer.BadParameter(f"Gold outputs not found for run_id={final_run_id}")

    examples = paths.examples_dir
    if format in {"markdown", "all"}:
        _copy_if_exists(
            gold_dir / "data_quality_report.md", examples / "sample_data_quality_report.md"
        )
        _copy_if_exists(
            gold_dir / "gold_metrics_summary.md", examples / "sample_gold_metrics_summary.md"
        )
        _copy_if_exists(gold_dir / "lineage.md", examples / "sample_lineage.md")
    if format in {"json", "all"}:
        _copy_if_exists(
            gold_dir / "data_quality_report.json", examples / "data_quality_report.json"
        )
        _copy_if_exists(gold_dir / "lineage.json", examples / "lineage.json")

    write_markdown_report(
        examples / "README.md",
        title="RetailDQ Demo Examples",
        sections={
            "Contents": (
                "- `sample_data_quality_report.md`\n"
                "- `sample_gold_metrics_summary.md`\n"
                "- `sample_lineage.md`\n"
                "- JSON report artifacts when requested"
            ),
            "Safety": "All examples are generated from deterministic synthetic data with no PII.",
        },
    )
    console.print(f"Reports written to [bold]{examples}[/bold]")


@app.command()
def demo(config: ConfigOption = Path("configs/local.yaml")) -> None:
    """Run a deterministic local end-to-end demo."""
    cfg = _load(config)
    run_id = f"{cfg.demo.run_id_prefix}-sample"
    paths = cfg.lakehouse_paths()
    if cfg.demo.clean_demo_outputs:
        paths.remove_demo_outputs(cfg.demo.run_id_prefix)
    result = run_pipeline(
        config=cfg,
        run_id=run_id,
        seed=cfg.generator.seed,
        generate_raw=True,
        fail_on_quality_threshold=True,
    )
    report(config=config, run_id=run_id, format="all")
    index_path = build_static_site(cfg, run_id)
    console.print(f"Demo complete for [bold]{result.run_id}[/bold]")
    console.print(f"Raw/silver/gold data: [bold]{paths.data_dir}[/bold]")
    console.print(f"Static site: [bold]{index_path}[/bold]")


@app.command("site-build")
def site_build(
    config: ConfigOption = Path("configs/local.yaml"),
    run_id: RunIdOption = None,
) -> None:
    """Build the static demo site from existing gold outputs."""
    cfg = _load(config)
    final_run_id = _resolve_run_id(config, run_id)
    index_path = build_static_site(cfg, final_run_id)
    console.print(f"Static site generated at [bold]{index_path}[/bold]")


@app.command()
def clean(
    config: ConfigOption = Path("configs/local.yaml"),
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Confirm deletion.")] = False,
) -> None:
    """Clean generated local artifacts."""
    cfg = _load(config)
    paths = cfg.lakehouse_paths()
    if not yes:
        confirmed = typer.confirm(f"Delete generated data under {paths.data_dir}?")
        if not confirmed:
            console.print("Clean cancelled.")
            raise typer.Exit(code=0)
    for target in [
        paths.raw_dir,
        paths.silver_dir,
        paths.gold_dir,
        paths.quarantine_dir,
        paths.metadata_dir,
        paths.site_dir,
        paths.warehouse_path,
    ]:
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    for layer in [paths.raw_dir, paths.silver_dir, paths.gold_dir, paths.quarantine_dir]:
        layer.mkdir(parents=True, exist_ok=True)
        (layer / ".gitkeep").write_text("keep\n", encoding="utf-8")
    console.print("Generated artifacts cleaned.")


@app.command("contracts")
def contracts_command(config: ConfigOption = Path("configs/local.yaml")) -> None:
    """Print loaded contract names."""
    cfg = _load(config)
    contracts = load_contracts(contract_dir_for(cfg))
    console.print("Contracts: " + ", ".join(contracts))
