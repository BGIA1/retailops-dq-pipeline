# RetailDQ Data Quality Report - docker-demo-sample

## Gate Summary

- Status: `pass`
- Invalid rate: `0.0413`
- Max invalid rate: `0.1500`
- Total records: `1040`
- Invalid records: `43`

## Rule Results

| run_id | entity | rule_id | rule_name | severity | status | failed_records | total_records | details |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| docker-demo-sample | channels | channels_channel_schema_present | schema validation | error | pass | 0 | 4 | Column channel must be present |
| docker-demo-sample | channels | channels_channel_not_null | null check | error | pass | 0 | 4 | channel must not be null |
| docker-demo-sample | channels | channels_channel_accepted_values | accepted values | error | pass | 0 | 4 | channel accepted values: web, mobile, marketplace, store |
| docker-demo-sample | channels | channels_description_schema_present | schema validation | error | pass | 0 | 4 | Column description must be present |
| docker-demo-sample | channels | channels_description_not_null | null check | error | pass | 0 | 4 | description must not be null |
| docker-demo-sample | channels | channels_channel_unique | primary key uniqueness | error | pass | 0 | 4 | channel duplicates are not allowed |
| docker-demo-sample | customers | customers_customer_id_schema_present | schema validation | error | pass | 0 | 90 | Column customer_id must be present |
| docker-demo-sample | customers | customers_customer_id_not_null | null check | error | pass | 0 | 90 | customer_id must not be null |
| docker-demo-sample | customers | customers_segment_schema_present | schema validation | error | pass | 0 | 90 | Column segment must be present |
| docker-demo-sample | customers | customers_segment_not_null | null check | error | pass | 0 | 90 | segment must not be null |
| docker-demo-sample | customers | customers_segment_accepted_values | accepted values | error | pass | 0 | 90 | segment accepted values: consumer, corporate, home_office |
| docker-demo-sample | customers | customers_region_schema_present | schema validation | error | pass | 0 | 90 | Column region must be present |
| docker-demo-sample | customers | customers_region_not_null | null check | error | pass | 0 | 90 | region must not be null |
| docker-demo-sample | customers | customers_region_accepted_values | accepted values | error | pass | 0 | 90 | region accepted values: north, central, south, online |
| docker-demo-sample | customers | customers_created_at_schema_present | schema validation | error | pass | 0 | 90 | Column created_at must be present |
| docker-demo-sample | customers | customers_created_at_not_null | null check | error | pass | 0 | 90 | created_at must not be null |
| docker-demo-sample | customers | customers_is_active_schema_present | schema validation | error | pass | 0 | 90 | Column is_active must be present |
| docker-demo-sample | customers | customers_is_active_not_null | null check | error | pass | 0 | 90 | is_active must not be null |
| docker-demo-sample | customers | customers_customer_id_unique | primary key uniqueness | error | pass | 0 | 90 | customer_id duplicates are not allowed |
| docker-demo-sample | customers | customers_created_at_not_future | future date check | error | pass | 0 | 90 | created_at must be <= 2026-06-11 |
| docker-demo-sample | products | products_product_id_schema_present | schema validation | error | pass | 0 | 50 | Column product_id must be present |
| docker-demo-sample | products | products_product_id_not_null | null check | error | pass | 0 | 50 | product_id must not be null |
| docker-demo-sample | products | products_category_schema_present | schema validation | error | pass | 0 | 50 | Column category must be present |
| docker-demo-sample | products | products_category_not_null | null check | error | pass | 0 | 50 | category must not be null |
| docker-demo-sample | products | products_category_accepted_values | accepted values | error | pass | 0 | 50 | category accepted values: electronics, grocery, apparel, home, sports, beauty |
| docker-demo-sample | products | products_base_price_schema_present | schema validation | error | pass | 0 | 50 | Column base_price must be present |
| docker-demo-sample | products | products_base_price_not_null | null check | error | pass | 0 | 50 | base_price must not be null |
| docker-demo-sample | products | products_base_price_min_value | numeric range | error | fail | 1 | 50 | base_price minimum: 0.01 |
| docker-demo-sample | products | products_base_price_max_value | numeric range | error | pass | 0 | 50 | base_price maximum: 5000.0 |
| docker-demo-sample | products | products_is_active_schema_present | schema validation | error | pass | 0 | 50 | Column is_active must be present |

## Invalid Records by Rule

| entity | rule_id | severity | invalid_records |
| --- | --- | --- | --- |
| order_items | order_items_order_id_fk | error | 1 |
| order_items | order_items_order_id_silver_fk | error | 14 |
| order_items | order_items_product_id_fk | error | 1 |
| order_items | order_items_product_id_not_null | error | 1 |
| order_items | order_items_product_id_silver_fk | error | 14 |
| order_items | order_items_quantity_min_value | error | 1 |
| order_items | order_items_unit_price_min_value | error | 1 |
| orders | orders_channel_accepted_values | error | 1 |
| orders | orders_channel_fk | error | 1 |
| orders | orders_customer_id_fk | error | 1 |
| orders | orders_customer_id_not_null | error | 1 |
| orders | orders_order_date_not_future | error | 1 |
| orders | orders_order_id_unique | error | 2 |
| orders | orders_order_status_accepted_values | error | 1 |
| orders | orders_store_id_silver_fk | error | 2 |
| products | products_base_price_min_value | error | 1 |
| stores | stores_region_accepted_values | error | 1 |

## Quarantine Strategy

Invalid records are persisted with rule ids, record ids when present, original payloads, severity, rejected timestamp, and source layer. They are isolated from silver/gold processing instead of breaking the batch.
