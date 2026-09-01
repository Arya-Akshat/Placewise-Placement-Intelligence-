CREATE TABLE IF NOT EXISTS placewise.silver.student_projects (
    id STRING, student_id STRING, project_id STRING, is_verified BOOLEAN
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for student_projects';\n