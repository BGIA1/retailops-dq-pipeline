CREATE SCHEMA IF NOT EXISTS silver;

CREATE OR REPLACE TABLE silver.customers AS
SELECT *
FROM read_parquet($customers_path);

CREATE OR REPLACE TABLE silver.products AS
SELECT *
FROM read_parquet($products_path);

CREATE OR REPLACE TABLE silver.stores AS
SELECT *
FROM read_parquet($stores_path);

CREATE OR REPLACE TABLE silver.channels AS
SELECT *
FROM read_parquet($channels_path);
