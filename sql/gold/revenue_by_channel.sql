CREATE OR REPLACE TABLE gold.revenue_by_channel AS
SELECT
  o.channel,
  ROUND(SUM(i.quantity * i.unit_price), 2) AS revenue
FROM silver.order_items AS i
JOIN silver.orders AS o
  ON i.order_id = o.order_id
WHERE o.order_status IN ('paid', 'shipped')
GROUP BY o.channel
ORDER BY revenue DESC;
