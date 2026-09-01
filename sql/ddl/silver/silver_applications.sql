CREATE TABLE IF NOT EXISTS placewise.silver.applications (
    id STRING, student_id STRING, job_posting_id STRING, application_status STRING, applied_at TIMESTAMP, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for applications';\n