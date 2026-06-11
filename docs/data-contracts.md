# Data Contracts

Contracts live in `contracts/*.yaml`. They define entity schemas, primary keys, foreign keys, accepted values, nullability, and numeric ranges.

## Entities

| Entity | Primary key | Notes |
| --- | --- | --- |
| `customers` | `customer_id` | Synthetic segment and region, no PII |
| `products` | `product_id` | Category and positive base price |
| `stores` | `store_id` | Generic regions and store types |
| `channels` | `channel` | Web, mobile, marketplace, store |
| `orders` | `order_id` | Header fact table |
| `order_items` | `order_item_id` | Line item fact table |

## Accepted Values

- Segments: `consumer`, `corporate`, `home_office`
- Regions: `north`, `central`, `south`, `online`
- Channels: `web`, `mobile`, `marketplace`, `store`
- Statuses: `created`, `paid`, `shipped`, `cancelled`, `refunded`
- Product categories: `electronics`, `grocery`, `apparel`, `home`, `sports`, `beauty`

## Foreign Keys

| Source | Target |
| --- | --- |
| `orders.customer_id` | `customers.customer_id` |
| `orders.store_id` | `stores.store_id` |
| `orders.channel` | `channels.channel` |
| `order_items.order_id` | `orders.order_id` |
| `order_items.product_id` | `products.product_id` |

## Contract Enforcement

The pipeline loads contracts at runtime and converts them into validation checks. Pandera is wired as a schema companion, while custom checks provide row-level quarantine payloads.
