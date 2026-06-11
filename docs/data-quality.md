# Data Quality

RetailDQ treats data quality as a pipeline gate, not a dashboard afterthought.

## Rule Types

| Rule | Purpose | Severity |
| --- | --- | --- |
| Schema presence | Required contract columns exist | error |
| Null checks | Required fields are populated | error |
| Primary key uniqueness | Duplicates do not enter silver | error |
| Accepted values | Catalog fields stay in approved domains | error |
| Numeric ranges | Quantity and prices are plausible | error |
| Future dates | Dates are not ahead of current UTC date | error |
| Referential integrity | Child records reference valid parent records | error |
| Freshness | Orders are recent enough for batch expectations | warning |
| Anomaly checks | Simple revenue spike detection | warning/report |

## Invalid Cases Generated

- Duplicate `order_id`
- Missing or nonexistent `customer_id`
- Nonexistent `product_id`
- `quantity <= 0`
- `unit_price < 0`
- Invalid `order_status`
- Invalid `channel`
- Future `order_date`
- Null required fields
- `order_items` without an order
- Products with invalid price
- Stores with invalid region

## Quarantine

Invalid rows are persisted under `data/quarantine/{run_id}` with:

- `run_id`
- `entity`
- `record_id`
- `rule_id`
- `rule_name`
- `severity`
- `rejection_reason`
- `rejected_at`
- `original_payload`
- `source_layer`

This supports the reviewer explanation: invalid records did not break the pipeline; they were isolated with traceability.

## Thresholds

`quality.max_invalid_rate` controls the maximum allowed invalid record rate. `retaildq run` can fail the batch when the threshold is exceeded using `--fail-on-quality-threshold`.

## Reports

Generated reports include:

- `data_quality_report.md`
- `data_quality_report.json`
- `invalid_record_counts.parquet`
- `data_quality_pass_fail_summary.parquet`
