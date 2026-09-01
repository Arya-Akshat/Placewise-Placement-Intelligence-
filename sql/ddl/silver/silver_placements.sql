CREATE TABLE IF NOT EXISTS placewise.silver.placements (
    id STRING, offer_id STRING, student_id STRING, company_id STRING, placement_date DATE, created_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for placements';\n