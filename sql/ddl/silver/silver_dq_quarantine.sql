CREATE TABLE IF NOT EXISTS placewise.silver.dq_quarantine (
    id STRING, table_name STRING, payload STRING, error_reason STRING, quarantined_at TIMESTAMP
) USING DELTA COMMENT 'Quarantine for bad records';\n