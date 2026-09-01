CREATE TABLE IF NOT EXISTS placewise.bronze.academic_programs_raw (
    id STRING,
    payload STRING,
    _ingested_at TIMESTAMP,
    _source_file STRING
) USING DELTA
COMMENT 'Raw ingestion table for academic_programs';\n