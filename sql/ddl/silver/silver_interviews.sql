CREATE TABLE IF NOT EXISTS placewise.silver.interviews (
    id STRING, application_id STRING, interview_round INT, interview_type STRING, overall_score DOUBLE, status STRING, scheduled_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for interviews';\n