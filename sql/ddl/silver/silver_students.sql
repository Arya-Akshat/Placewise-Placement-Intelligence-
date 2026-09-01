CREATE TABLE IF NOT EXISTS placewise.silver.students (
    id STRING, student_id STRING, first_name STRING, last_name STRING, email STRING, phone STRING, department_id STRING, cohort_id STRING, cgpa DOUBLE, percentage DOUBLE, attendance_percentage DOUBLE, placement_status STRING, created_at TIMESTAMP, updated_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for students';\n