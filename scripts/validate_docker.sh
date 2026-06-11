#!/usr/bin/env bash
set -euo pipefail

docker build -t retaildq-lakehouse .
docker run --rm retaildq-lakehouse retaildq --help
docker compose run --rm retaildq retaildq demo --config configs/docker.yaml
