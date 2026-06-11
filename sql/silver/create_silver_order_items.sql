CREATE SCHEMA IF NOT EXISTS silver;

CREATE OR REPLACE TABLE silver.order_items AS
SELECT
  order_item_id,
  order_id,
  product_id,
  quantity,
  unit_price,
  run_id
FROM read_parquet($order_items_path);
