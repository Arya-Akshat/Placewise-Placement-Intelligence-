CREATE TABLE IF NOT EXISTS placewise.silver.companies (
    id STRING, company_name STRING, industry STRING, website STRING, tier STRING, created_at TIMESTAMP, updated_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for companies';\n