#!/usr/bin/env bash
set -euo pipefail

echo "Running RetailDQ smoke test..."
retaildq --help
retaildq demo --config configs/local.yaml
retaildq site-build --config configs/local.yaml
echo "Smoke test completed."
