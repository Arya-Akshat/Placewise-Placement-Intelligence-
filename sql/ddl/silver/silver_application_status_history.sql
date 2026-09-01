CREATE TABLE IF NOT EXISTS placewise.silver.application_status_history (
    id STRING, application_id STRING, status STRING, updated_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for application_status_history';\n