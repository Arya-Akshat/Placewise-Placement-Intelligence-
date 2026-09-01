CREATE TABLE IF NOT EXISTS placewise.silver.projects (
    id STRING, project_title STRING, difficulty_level STRING, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for projects';\n