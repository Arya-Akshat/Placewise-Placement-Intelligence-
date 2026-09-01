CREATE TABLE IF NOT EXISTS placewise.silver.job_required_skills (
    id STRING, job_posting_id STRING, skill_id STRING, is_mandatory BOOLEAN, importance_weight DOUBLE, required_score DOUBLE, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for job_required_skills';\n