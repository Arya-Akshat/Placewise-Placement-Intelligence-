CREATE TABLE IF NOT EXISTS placewise.silver.job_roles (
    id STRING, role_name STRING, description STRING, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for job_roles';\n