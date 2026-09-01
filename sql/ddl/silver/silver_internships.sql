CREATE TABLE IF NOT EXISTS placewise.silver.internships (
    id STRING, student_id STRING, company_name STRING, duration_months INT, has_ppo BOOLEAN, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for internships';\n