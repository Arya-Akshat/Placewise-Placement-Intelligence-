CREATE TABLE IF NOT EXISTS placewise.bronze.placement_events_raw (
    id STRING,
    payload STRING,
    _ingested_at TIMESTAMP,
    _source_file STRING
) USING DELTA
COMMENT 'Raw ingestion table for placement_events';\n