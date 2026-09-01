CREATE TABLE IF NOT EXISTS placewise.silver.offers (
    id STRING, application_id STRING, offer_ctc DOUBLE, offer_status STRING, accepted_at TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for offers';\n