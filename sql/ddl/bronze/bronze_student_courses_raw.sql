CREATE TABLE IF NOT EXISTS placewise.bronze.student_courses_raw (
    id STRING,
    payload STRING,
    _ingested_at TIMESTAMP,
    _source_file STRING
) USING DELTA
COMMENT 'Raw ingestion table for student_courses';\n