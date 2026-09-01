CREATE TABLE IF NOT EXISTS placewise.silver.job_postings (
    id STRING, company_id STRING, role_id STRING, title STRING, location STRING, expected_ctc DOUBLE, min_cgpa DOUBLE, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for job_postings';\n