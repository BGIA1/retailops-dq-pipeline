Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Running RetailDQ smoke test..."
retaildq --help
retaildq demo --config configs/local.yaml
retaildq site-build --config configs/local.yaml
Write-Host "Smoke test completed."
