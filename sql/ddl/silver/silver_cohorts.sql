CREATE TABLE IF NOT EXISTS placewise.silver.cohorts (
    id STRING, cohort_name STRING, start_year INT, end_year INT, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for cohorts';\n