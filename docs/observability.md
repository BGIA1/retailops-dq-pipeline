# Observability

RetailDQ provides local observability artifacts suitable for a portfolio V1.

## Artifacts

| Artifact | Location |
| --- | --- |
| Run metadata | `data/gold/{run_id}/pipeline_run_metadata.json` |
| Run history | `data/_metadata/runs.jsonl` |
| Watermark | `data/_metadata/watermarks.json` |
| Quality report | `data/gold/{run_id}/data_quality_report.md` |
| Quarantine records | `data/quarantine/{run_id}` |
| Lineage | `data/gold/{run_id}/lineage.md` |
| DuckDB warehouse | `data/retaildq.duckdb` |

## Failure Modes

- Missing raw entity files: validation fails with a file error.
- Contract violations: rows are quarantined.
- Invalid rate over threshold: the pipeline raises a quality threshold error.
- Docker or CI failures: the build stops before a deployment path.

## Cloud Mapping

In Azure, these artifacts map to ADLS paths and Container Apps Job logs in Log Analytics. This repository does not claim full enterprise observability; it implements a clear local observability baseline.
