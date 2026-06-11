Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

docker build -t retaildq-lakehouse .
docker run --rm retaildq-lakehouse retaildq --help
docker compose run --rm retaildq retaildq demo --config configs/docker.yaml
