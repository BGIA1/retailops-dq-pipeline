# Portfolio Packaging

## Summary

RetailDQ is a pipeline-first retail lakehouse project showing data engineering reliability controls: generation, contracts, quality gates, quarantine, silver/gold layers, observability, CI/CD, Docker, and Azure readiness.

## CV Bullets: Data Engineer

- Built a Python lakehouse pipeline with raw/silver/gold layers using Polars, DuckDB, and deterministic synthetic retail data.
- Implemented data contracts, quality gates, invalid record quarantine, referential integrity checks, and gold marts.
- Added local observability with run metadata, lineage, DQ reports, watermarks, and DuckDB registration.

## CV Bullets: Azure Data Engineer

- Designed Azure deployment readiness with Bicep for ADLS Gen2, ACR, Log Analytics, Container Apps Environment, and Container Apps Job.
- Prepared secure GitHub Actions OIDC flow without long-lived secrets.
- Documented cost controls, shutdown plan, least privilege, and manual deployment guardrails.

## CV Bullets: Analytics Engineer

- Modeled trusted gold metrics including revenue by day/channel/store, order KPIs, top products, and DQ summaries.
- Used contracts and tests to protect semantic consistency before analytical consumption.
- Published static synthetic demo artifacts suitable for GitHub Pages.

## 60-Second Interview Pitch

RetailDQ is a local-first data pipeline that demonstrates how I approach data reliability. It generates synthetic retail data, lands it raw by run id, validates it against contracts, quarantines invalid records with rule-level traceability, builds clean silver tables, and publishes gold metrics. CI runs linting, typing, tests, a deterministic demo, and Docker build validation. The Azure deployment path is prepared with Bicep and OIDC but intentionally manual to avoid accidental cost or secret exposure.

## Technical Deep Dive

The important design choice is that quality checks produce row-level quarantine artifacts instead of only aggregate failures. That makes bad data explainable while allowing valid records to continue through the batch. The pipeline uses run partitions and watermarks to simulate incremental processing locally, then maps that model to ADLS paths for cloud deployment.

## Honest Limitations

- Synthetic data only.
- Batch only.
- No real Azure deployment performed.
- No full monitoring suite.
- No interactive dashboard in V1.

## Roadmap

- Optional Azure storage adapter.
- Contract compatibility and schema evolution checks.
- Historical DQ trend marts.
- Larger synthetic volume benchmarking.
