#!/usr/bin/env bash
set -euo pipefail

python -m pip install -e ".[dev]"
retaildq --help
retaildq demo --config configs/local.yaml
retaildq validate --config configs/local.yaml
retaildq report --config configs/local.yaml --format all
retaildq site-build --config configs/local.yaml
ruff check .
ruff format --check .
mypy src
pytest -q
pytest --cov=retaildq --cov-report=term-missing
