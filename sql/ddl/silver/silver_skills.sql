CREATE TABLE IF NOT EXISTS placewise.silver.skills (
    id STRING, skill_name STRING, skill_category STRING, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for skills';\n