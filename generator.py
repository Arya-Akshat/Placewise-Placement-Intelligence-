import os

BASE_DIR = "/Users/gurudev/Desktop/VS Code/Dunno/Placewise"

sql_files = {
    # 1. Schemas
    "databricks/schemas/create_schemas.sql": """
CREATE SCHEMA IF NOT EXISTS placewise.bronze COMMENT 'Raw ingestion layer';
CREATE SCHEMA IF NOT EXISTS placewise.silver COMMENT 'Cleaned, validated layer';
CREATE SCHEMA IF NOT EXISTS placewise.gold COMMENT 'Analytical and fact layer';
CREATE SCHEMA IF NOT EXISTS placewise.semantic COMMENT 'Semantic views for reporting';
CREATE SCHEMA IF NOT EXISTS placewise.sandbox COMMENT 'Ad-hoc analysis workspace';
""",
    # 8. Catalog
    "databricks/catalogs/catalog_setup.sql": """
CREATE CATALOG IF NOT EXISTS placewise COMMENT 'Placewise Unity Catalog';
ALTER CATALOG placewise OWNER TO `admin`;
USE CATALOG placewise;
""",
}

bronze_tables = [
    "students", "companies", "departments", "academic_programs", "cohorts",
    "job_postings", "job_roles", "applications", "interviews", "offers",
    "placements", "skills", "student_skills", "job_required_skills", "projects",
    "student_projects", "internships", "application_status_history",
    "student_certifications", "student_courses", "placement_events"
]

for bt in bronze_tables:
    sql_files[f"sql/ddl/bronze/bronze_{bt}_raw.sql"] = f"""
CREATE TABLE IF NOT EXISTS placewise.bronze.{bt}_raw (
    id STRING,
    payload STRING,
    _ingested_at TIMESTAMP,
    _source_file STRING
) USING DELTA
COMMENT 'Raw ingestion table for {bt}';
"""

# 3. Silver
silver_tables = {
    "students": "id STRING, student_id STRING, first_name STRING, last_name STRING, email STRING, phone STRING, department_id STRING, cohort_id STRING, cgpa DOUBLE, percentage DOUBLE, attendance_percentage DOUBLE, placement_status STRING, created_at TIMESTAMP, updated_at TIMESTAMP",
    "companies": "id STRING, company_name STRING, industry STRING, website STRING, tier STRING, created_at TIMESTAMP, updated_at TIMESTAMP",
    "departments": "id STRING, department_name STRING, created_at TIMESTAMP",
    "academic_programs": "id STRING, program_name STRING, department_id STRING, duration_years INT, created_at TIMESTAMP",
    "cohorts": "id STRING, cohort_name STRING, start_year INT, end_year INT, created_at TIMESTAMP",
    "job_roles": "id STRING, role_name STRING, description STRING, created_at TIMESTAMP",
    "job_postings": "id STRING, company_id STRING, role_id STRING, title STRING, location STRING, expected_ctc DOUBLE, min_cgpa DOUBLE, created_at TIMESTAMP",
    "job_posting_departments": "id STRING, job_posting_id STRING, department_id STRING, created_at TIMESTAMP",
    "skills": "id STRING, skill_name STRING, skill_category STRING, created_at TIMESTAMP",
    "student_skills": "id STRING, student_id STRING, skill_id STRING, proficiency_level STRING, is_verified BOOLEAN, created_at TIMESTAMP",
    "job_required_skills": "id STRING, job_posting_id STRING, skill_id STRING, is_mandatory BOOLEAN, importance_weight DOUBLE, required_score DOUBLE, created_at TIMESTAMP",
    "applications": "id STRING, student_id STRING, job_posting_id STRING, application_status STRING, applied_at TIMESTAMP, created_at TIMESTAMP",
    "application_status_history": "id STRING, application_id STRING, status STRING, updated_at TIMESTAMP",
    "interviews": "id STRING, application_id STRING, interview_round INT, interview_type STRING, overall_score DOUBLE, status STRING, scheduled_at TIMESTAMP",
    "offers": "id STRING, application_id STRING, offer_ctc DOUBLE, offer_status STRING, accepted_at TIMESTAMP",
    "placements": "id STRING, offer_id STRING, student_id STRING, company_id STRING, placement_date DATE, created_at TIMESTAMP",
    "projects": "id STRING, project_title STRING, difficulty_level STRING, created_at TIMESTAMP",
    "student_projects": "id STRING, student_id STRING, project_id STRING, is_verified BOOLEAN",
    "internships": "id STRING, student_id STRING, company_name STRING, duration_months INT, has_ppo BOOLEAN, created_at TIMESTAMP",
    "student_certifications": "id STRING, student_id STRING, certification_name STRING, is_verified BOOLEAN",
    "student_courses": "id STRING, student_id STRING, course_name STRING, grade STRING",
    "placement_events": "id STRING, event_name STRING, event_date DATE, type STRING"
}

for st, cols in silver_tables.items():
    sql_files[f"sql/ddl/silver/silver_{st}.sql"] = f"""
CREATE TABLE IF NOT EXISTS placewise.silver.{st} (
    {cols}
) USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
COMMENT 'Primary Key: id. Cleaned table for {st}';
"""

sql_files["sql/ddl/silver/silver_dq_report.sql"] = """
CREATE TABLE IF NOT EXISTS placewise.silver.dq_report (
    run_id STRING, table_name STRING, rule_name STRING, failed_count INT, total_count INT, run_time TIMESTAMP
) USING DELTA COMMENT 'Data quality report';
"""
sql_files["sql/ddl/silver/silver_dq_quarantine.sql"] = """
CREATE TABLE IF NOT EXISTS placewise.silver.dq_quarantine (
    id STRING, table_name STRING, payload STRING, error_reason STRING, quarantined_at TIMESTAMP
) USING DELTA COMMENT 'Quarantine for bad records';
"""

# 4. Gold DDL
gold_dims = ["date", "student", "department", "program", "cohort", "company", "job_posting", "job_role", "skill", "project"]
gold_facts = ["application", "interview", "offer", "placement", "student_skill", "job_skill_requirement", "internship"]

for gd in gold_dims:
    sql_files[f"sql/ddl/gold/gold_dim_{gd}.sql"] = f"CREATE TABLE IF NOT EXISTS placewise.gold.dim_{gd} (id STRING, created_at TIMESTAMP) USING DELTA COMMENT 'Dimension: {gd}';"
for gf in gold_facts:
    sql_files[f"sql/ddl/gold/gold_fact_{gf}.sql"] = f"CREATE TABLE IF NOT EXISTS placewise.gold.fact_{gf} (id STRING, created_at TIMESTAMP) USING DELTA COMMENT 'Fact: {gf}';"

# Derived Gold DDL
sql_files["sql/ddl/gold/gold_student_placement_profile.sql"] = """
CREATE OR REPLACE TABLE placewise.gold.student_placement_profile AS
SELECT 
    s.student_id,
    ROUND(LEAST(100, GREATEST(0, (COALESCE(s.cgpa,0)/10.0)*70 + (COALESCE(s.percentage,0)/100.0)*20 + (COALESCE(s.attendance_percentage,0)/100.0)*10)), 2) AS academic_score,
    COALESCE(ss.skill_score, 0) AS skill_score,
    COALESCE(i.internship_score, 0) AS internship_score,
    COALESCE(p.project_score, 0) AS project_score,
    COALESCE(iv.interview_score, 0) AS interview_score,
    COALESCE(ac.application_conversion_score, 0) AS application_conversion_score,
    ROUND(
        (ROUND(LEAST(100, GREATEST(0, (COALESCE(s.cgpa,0)/10.0)*70 + (COALESCE(s.percentage,0)/100.0)*20 + (COALESCE(s.attendance_percentage,0)/100.0)*10)), 2) * 0.20) +
        (COALESCE(ss.skill_score, 0) * 0.25) +
        (COALESCE(i.internship_score, 0) * 0.10) +
        (COALESCE(p.project_score, 0) * 0.10) +
        (COALESCE(iv.interview_score, 0) * 0.20) +
        (COALESCE(ac.application_conversion_score, 0) * 0.15), 
    2) AS placement_readiness_score
FROM placewise.silver.students s
LEFT JOIN (SELECT student_id, AVG(CASE WHEN is_verified THEN 100 ELSE 50 END) as skill_score FROM placewise.silver.student_skills GROUP BY student_id) ss ON s.student_id = ss.student_id
LEFT JOIN (SELECT student_id, SUM(duration_months * 10 + CASE WHEN has_ppo THEN 20 ELSE 0 END) as internship_score FROM placewise.silver.internships GROUP BY student_id) i ON s.student_id = i.student_id
LEFT JOIN (SELECT student_id, COUNT(project_id)*20 as project_score FROM placewise.silver.student_projects GROUP BY student_id) p ON s.student_id = p.student_id
LEFT JOIN (SELECT a.student_id, AVG(i.overall_score) as interview_score FROM placewise.silver.interviews i JOIN placewise.silver.applications a ON i.application_id = a.id GROUP BY a.student_id) iv ON s.student_id = iv.student_id
LEFT JOIN (SELECT student_id, CASE WHEN COUNT(id) > 0 THEN ROUND(SUM(CASE WHEN application_status = 'SHORTLISTED' THEN 1 ELSE 0 END) * 100.0 / COUNT(id), 2) ELSE 0 END as application_conversion_score FROM placewise.silver.applications GROUP BY student_id) ac ON s.student_id = ac.student_id;
"""

sql_files["sql/ddl/gold/gold_student_job_skill_match.sql"] = """
CREATE OR REPLACE TABLE placewise.gold.student_job_skill_match AS
SELECT 
    ss.student_id, jrs.job_posting_id,
    SUM(jrs.importance_weight * GREATEST(0, jrs.required_score - COALESCE(ss.student_score, 0))) / NULLIF(SUM(jrs.importance_weight * jrs.required_score), 0) AS weighted_deficit,
    100 - (SUM(jrs.importance_weight * GREATEST(0, jrs.required_score - COALESCE(ss.student_score, 0))) / NULLIF(SUM(jrs.importance_weight * jrs.required_score), 0) * 100) AS skill_match_percentage,
    SUM(CASE WHEN jrs.is_mandatory AND ss.student_score IS NULL THEN 1 ELSE 0 END) AS missing_mandatory_skill_count
FROM placewise.silver.job_required_skills jrs
CROSS JOIN (SELECT DISTINCT student_id FROM placewise.silver.students) st
LEFT JOIN (SELECT student_id, skill_id, 100 as student_score FROM placewise.silver.student_skills) ss 
  ON st.student_id = ss.student_id AND jrs.skill_id = ss.skill_id
GROUP BY ss.student_id, jrs.job_posting_id;
"""

sql_files["sql/ddl/gold/gold_student_application_funnel.sql"] = """
CREATE OR REPLACE TABLE placewise.gold.student_application_funnel AS
SELECT 
    student_id,
    COUNT(id) AS applications_count,
    SUM(CASE WHEN application_status = 'SHORTLISTED' THEN 1 ELSE 0 END) AS shortlisted_count,
    CASE WHEN COUNT(id) > 0 THEN ROUND(SUM(CASE WHEN application_status = 'SHORTLISTED' THEN 1 ELSE 0 END) * 100.0 / COUNT(id), 2) ELSE NULL END AS application_to_shortlist_rate
FROM placewise.silver.applications
GROUP BY student_id;
"""

gold_others = ["company_hiring_profile", "role_demand_profile", "skill_demand_profile", "department_placement_performance"]
for go in gold_others:
    sql_files[f"sql/ddl/gold/gold_{go}.sql"] = f"CREATE OR REPLACE TABLE placewise.gold.{go} AS SELECT 'stub' as stub_col;"

# 5. Silver Transformations (MERGE patterns)
transform_entities = ["students", "companies", "applications", "interviews", "offers", "placements", "skills", "job_postings", "internships"]
for te in transform_entities:
    sql_files[f"sql/transformations/bronze_to_silver_{te}.sql"] = f"""
MERGE INTO placewise.silver.{te} target
USING (
    SELECT id, _ingested_at, payload FROM placewise.bronze.{te}_raw
) source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
"""

# 6. Gold Transformations
gold_transforms = [
    "student_placement_profile", "student_job_skill_match", 
    "company_hiring_profile", "department_placement_performance", "skill_demand_profile"
]
for gt in gold_transforms:
    sql_files[f"sql/transformations/silver_to_gold_{gt}.sql"] = f"""
-- Refresh logic for {gt}
-- Usually implemented via dbt or CREATE OR REPLACE TABLE in Databricks tasks.
-- See sql/ddl/gold/gold_{gt}.sql for full definition.
"""

sql_files["sql/transformations/silver_to_gold_dim_date.sql"] = """
CREATE OR REPLACE TABLE placewise.gold.dim_date AS
WITH RECURSIVE dates AS (
    SELECT CAST('2010-01-01' AS DATE) AS date_val
    UNION ALL
    SELECT date_add(date_val, 1) FROM dates WHERE date_val < CAST('2035-12-31' AS DATE)
)
SELECT 
    date_val AS date,
    YEAR(date_val) AS year,
    MONTH(date_val) AS month,
    DAY(date_val) AS day,
    CONCAT('AY', YEAR(date_add(date_val, -6)), '-', SUBSTRING(CAST(YEAR(date_add(date_val, 6)) AS STRING), 3, 2)) AS academic_year,
    CONCAT('PS', YEAR(date_add(date_val, -7))) AS placement_season,
    CASE WHEN MONTH(date_val) IN (8,9,10,11,12) THEN 1 ELSE 2 END AS semester
FROM dates;
"""

# 7. Semantic layer
semantic_views = [
    "student_placement_metrics", "company_hiring_metrics", 
    "department_placement_metrics", "skill_demand_metrics", 
    "application_funnel_metrics", "student_skill_match_metrics"
]
for sv in semantic_views:
    sql_files[f"sql/ddl/semantic/semantic_{sv}.sql"] = f"""
CREATE OR REPLACE VIEW placewise.semantic.{sv} AS
SELECT * FROM placewise.gold.{sv.replace('_metrics', '_profile')};
"""

# Write files
for rel_path, content in sql_files.items():
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content.strip() + "\\n")

print(f"Successfully generated {len(sql_files)} SQL files at {BASE_DIR}")
