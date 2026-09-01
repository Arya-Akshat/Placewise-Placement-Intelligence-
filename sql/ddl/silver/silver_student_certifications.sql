CREATE TABLE IF NOT EXISTS placewise.silver.student_certifications (
    id STRING, student_id STRING, certification_name STRING, is_verified BOOLEAN
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for student_certifications';\n