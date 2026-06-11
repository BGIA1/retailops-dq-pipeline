from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from retaildq.cli import app


def test_demo_command_runs_end_to_end(temp_config_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["demo", "--config", str(temp_config_path)])

    assert result.exit_code == 0, result.output
    project = temp_config_path.parent.parent
    assert (project / "site" / "generated" / "index.html").exists()
    assert (project / "examples" / "demo" / "sample_data_quality_report.md").exists()
