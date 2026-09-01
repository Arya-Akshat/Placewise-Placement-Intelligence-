CREATE TABLE IF NOT EXISTS placewise.silver.student_skills (
    id STRING, student_id STRING, skill_id STRING, proficiency_level STRING, is_verified BOOLEAN, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for student_skills';\n