CREATE TABLE IF NOT EXISTS placewise.bronze.companies_raw (
    id STRING,
    payload STRING,
    _ingested_at TIMESTAMP,
    _source_file STRING
) USING DELTA
COMMENT 'Raw ingestion table for companies';\n