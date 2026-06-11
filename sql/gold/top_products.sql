CREATE OR REPLACE TABLE gold.top_products_by_revenue AS
SELECT
  i.product_id,
  p.category,
  ROUND(SUM(i.quantity * i.unit_price), 2) AS revenue
FROM silver.order_items AS i
JOIN silver.orders AS o
  ON i.order_id = o.order_id
JOIN silver.products AS p
  ON i.product_id = p.product_id
WHERE o.order_status IN ('paid', 'shipped')
GROUP BY i.product_id, p.category
ORDER BY revenue DESC
LIMIT 10;

CREATE OR REPLACE TABLE gold.top_products_by_quantity AS
SELECT
  i.product_id,
  p.category,
  SUM(i.quantity) AS quantity
FROM silver.order_items AS i
JOIN silver.orders AS o
  ON i.order_id = o.order_id
JOIN silver.products AS p
  ON i.product_id = p.product_id
WHERE o.order_status IN ('paid', 'shipped')
GROUP BY i.product_id, p.category
ORDER BY quantity DESC
LIMIT 10;
