CREATE TABLE IF NOT EXISTS placewise.silver.dq_report (
    run_id STRING, table_name STRING, rule_name STRING, failed_count INT, total_count INT, run_time TIMESTAMP
) USING DELTA COMMENT 'Data quality report';\n