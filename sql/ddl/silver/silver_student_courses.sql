CREATE TABLE IF NOT EXISTS placewise.silver.student_courses (
    id STRING, student_id STRING, course_name STRING, grade STRING
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for student_courses';\n