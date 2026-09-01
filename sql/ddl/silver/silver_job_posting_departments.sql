CREATE TABLE IF NOT EXISTS placewise.silver.job_posting_departments (
    id STRING, job_posting_id STRING, department_id STRING, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for job_posting_departments';\n