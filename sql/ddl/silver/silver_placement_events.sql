CREATE TABLE IF NOT EXISTS placewise.silver.placement_events (
    id STRING, event_name STRING, event_date DATE, type STRING
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for placement_events';\n