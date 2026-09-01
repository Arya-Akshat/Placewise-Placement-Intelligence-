CREATE TABLE IF NOT EXISTS placewise.silver.departments (
    id STRING, department_name STRING, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for departments';\n