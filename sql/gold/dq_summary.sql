CREATE OR REPLACE TABLE gold.invalid_record_counts AS
SELECT
  entity,
  rule_id,
  severity,
  COUNT(*) AS invalid_records
FROM read_parquet($quarantine_path)
GROUP BY entity, rule_id, severity
ORDER BY entity, rule_id;

CREATE OR REPLACE TABLE gold.data_quality_pass_fail_summary AS
SELECT *
FROM read_parquet($dq_summary_path);
