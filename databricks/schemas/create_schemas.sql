CREATE SCHEMA IF NOT EXISTS placewise.bronze COMMENT 'Raw ingestion layer';
CREATE SCHEMA IF NOT EXISTS placewise.silver COMMENT 'Cleaned, validated layer';
CREATE SCHEMA IF NOT EXISTS placewise.gold COMMENT 'Analytical and fact layer';
CREATE SCHEMA IF NOT EXISTS placewise.semantic COMMENT 'Semantic views for reporting';
CREATE SCHEMA IF NOT EXISTS placewise.sandbox COMMENT 'Ad-hoc analysis workspace';\n