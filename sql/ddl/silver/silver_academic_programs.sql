CREATE TABLE IF NOT EXISTS placewise.silver.academic_programs (
    id STRING, program_name STRING, department_id STRING, duration_years INT, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for academic_programs';\n