# Local Development

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -e ".[dev]"
```

## Validate

```powershell
.\.venv\Scripts\retaildq.exe --help
.\.venv\Scripts\retaildq.exe demo --config configs/local.yaml
.\.venv\Scripts\retaildq.exe validate --config configs/local.yaml
.\.venv\Scripts\retaildq.exe report --config configs/local.yaml --format all
.\.venv\Scripts\retaildq.exe site-build --config configs/local.yaml
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\mypy.exe src
.\.venv\Scripts\pytest.exe -q
```

## Generated Artifacts

Generated data under raw, silver, gold, quarantine, local DuckDB files, and site outputs are ignored by git. Sample reports under `examples/demo` can be committed when regenerated intentionally from synthetic data.
