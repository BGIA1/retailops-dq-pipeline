CREATE OR REPLACE TABLE gold.revenue_by_store AS
SELECT
  o.store_id,
  s.region,
  ROUND(SUM(i.quantity * i.unit_price), 2) AS revenue
FROM silver.order_items AS i
JOIN silver.orders AS o
  ON i.order_id = o.order_id
JOIN silver.stores AS s
  ON o.store_id = s.store_id
WHERE o.order_status IN ('paid', 'shipped')
GROUP BY o.store_id, s.region
ORDER BY revenue DESC;
