CREATE TABLE IF NOT EXISTS placewise.bronze.student_skills_raw (
    id STRING,
    payload STRING,
    _ingested_at TIMESTAMP,
    _source_file STRING
) USING DELTA
COMMENT 'Raw ingestion table for student_skills';\n