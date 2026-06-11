# RetailDQ Gold Metrics Summary - docker-demo-sample

## Revenue by Day

| order_date | revenue |
| --- | --- |
| 2026-06-02 | 47162.15 |
| 2026-06-03 | 69319.0 |
| 2026-06-04 | 105656.97 |
| 2026-06-05 | 94024.31 |
| 2026-06-06 | 39681.28 |
| 2026-06-07 | 72787.0 |
| 2026-06-08 | 68445.78 |
| 2026-06-09 | 32064.65 |
| 2026-06-10 | 43899.81 |
| 2026-06-11 | 53166.88 |

## Revenue by Channel

| channel | revenue |
| --- | --- |
| web | 247384.69 |
| mobile | 166043.49 |
| store | 114474.8 |
| marketplace | 98304.85 |

## Average Order Value

| metric | value | order_count |
| --- | --- | --- |
| average_order_value | 3403.3 | 184 |

## Top Products by Revenue

| product_id | category | revenue |
| --- | --- | --- |
| SKU-000045 | electronics | 32056.04 |
| SKU-000009 | sports | 31800.5 |
| SKU-000012 | grocery | 29108.69 |
| SKU-000026 | beauty | 25721.35 |
| SKU-000037 | home | 24966.68 |
| SKU-000032 | beauty | 24519.95 |
| SKU-000033 | beauty | 23383.48 |
| SKU-000050 | grocery | 22484.91 |
| SKU-000007 | electronics | 21223.53 |
| SKU-000042 | home | 19022.66 |

## Data Quality Summary

| status | passed | invalid_rate | max_invalid_rate | total_records | invalid_records | quarantine_path |
| --- | --- | --- | --- | --- | --- | --- |
| pass | True | 0.041346153846153845 | 0.15 | 1040 | 43 | /app/data/quarantine/docker-demo-sample |
