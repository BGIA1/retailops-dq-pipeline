CREATE OR REPLACE TABLE gold.order_count_by_day AS
SELECT
  order_date,
  COUNT(*) AS order_count
FROM silver.orders
GROUP BY order_date
ORDER BY order_date;

CREATE OR REPLACE TABLE gold.average_order_value AS
WITH order_totals AS (
  SELECT
    o.order_id,
    SUM(i.quantity * i.unit_price) AS order_revenue
  FROM silver.order_items AS i
  JOIN silver.orders AS o
    ON i.order_id = o.order_id
  WHERE o.order_status IN ('paid', 'shipped')
  GROUP BY o.order_id
)
SELECT
  'average_order_value' AS metric,
  ROUND(AVG(order_revenue), 2) AS value,
  COUNT(*) AS order_count
FROM order_totals;
