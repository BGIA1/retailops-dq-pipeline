# RetailDQ Lineage - docker-demo-sample

- `customers`: `raw.customers` -> `silver.customers`
- `products`: `raw.products` -> `silver.products`
- `stores`: `raw.stores` -> `silver.stores`
- `channels`: `raw.channels` -> `silver.channels`
- `orders`: `raw.orders` -> `silver.orders`
- `order_items`: `raw.order_items` -> `silver.order_items`
- `revenue_by_day`: `silver.orders` -> `silver.order_items` -> `gold.revenue_by_day`
- `revenue_by_channel`: `silver.orders` -> `silver.order_items` -> `gold.revenue_by_channel`
- `revenue_by_store`: `silver.orders` -> `silver.order_items` -> `silver.stores` -> `gold.revenue_by_store`
- `top_products`: `silver.order_items` -> `silver.products` -> `gold.top_products_by_revenue` -> `gold.top_products_by_quantity`
- `data_quality`: `raw.*` -> `quarantine.*` -> `gold.data_quality_pass_fail_summary`
