CREATE SCHEMA IF NOT EXISTS silver;

CREATE OR REPLACE TABLE silver.orders AS
SELECT
  order_id,
  customer_id,
  store_id,
  channel,
  order_status,
  order_date,
  created_at,
  run_id
FROM read_parquet($orders_path);
