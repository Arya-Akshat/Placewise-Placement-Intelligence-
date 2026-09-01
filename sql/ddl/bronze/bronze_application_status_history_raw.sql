CREATE TABLE IF NOT EXISTS placewise.bronze.application_status_history_raw (
    id STRING,
    payload STRING,
    _ingested_at TIMESTAMP,
    _source_file STRING
) USING DELTA
COMMENT 'Raw ingestion table for application_status_history';\n