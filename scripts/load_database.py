"""
PLACEWISE — Relational Database Loader (DuckDB / SQLite / Parquet)
==================================================================
Loads all generated synthetic CSV data (2.19M rows) into a relational
database with full Medallion architecture (bronze, silver, gold, semantic).
"""

import os, sys, glob, time
import duckdb
import pandas as pd

DB_FILE = "data/placewise.duckdb"
CSV_DIR = "data/synthetic"

print("=" * 65)
print("  PLACEWISE — Loading Synthetic Data into Relational DB")
print(f"  Target DB: {DB_FILE}")
print(f"  Source:    {CSV_DIR}")
print("=" * 65)

start_time = time.time()

# Connect to DuckDB persistent database
con = duckdb.connect(DB_FILE)

# 1. Create schemas
print("\n[1/4] Creating Medallion Schemas...")
for schema in ["bronze", "silver", "gold", "semantic", "sandbox"]:
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
print("  ✓ Created schemas: bronze, silver, gold, semantic, sandbox")

# 2. Load Bronze and Silver tables from CSVs
print("\n[2/4] Loading CSVs into Bronze and Silver layers...")
csv_files = sorted(glob.glob(f"{CSV_DIR}/*.csv"))

for fpath in csv_files:
    tname = os.path.basename(fpath).replace(".csv", "")
    
    # Load into silver
    con.execute(f"""
        CREATE OR REPLACE TABLE silver.{tname} AS 
        SELECT * FROM read_csv_auto('{fpath}', header=True);
    """)
    
    # Load into bronze raw with ingestion metadata
    con.execute(f"""
        CREATE OR REPLACE TABLE bronze.{tname}_raw AS 
        SELECT *, 
               current_timestamp AS _ingested_at, 
               '{fpath}' AS _source_file 
        FROM read_csv_auto('{fpath}', header=True);
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM silver.{tname}").fetchone()[0]
    print(f"  ✓ silver.{tname:<32} ({count:>10,} rows)")

# 3. Build Gold Analytical Layer
print("\n[3/4] Building Gold Analytical Layer & Derived Intelligence Profiles...")

# A. Student Placement Profile (Primary Intelligence Dataset)
con.execute("""
CREATE OR REPLACE TABLE gold.student_placement_profile AS
WITH
base AS (
  SELECT
    s.student_id,
    s.full_name,
    s.gender,
    s.university_roll_no,
    s.cohort_id,
    s.department_id,
    s.program_id,
    s.current_semester,
    s.graduation_year,
    s.placement_status,
    s.preferred_role,
    s.preferred_location,
    s.work_authorization,
    COALESCE(s.cgpa, 0.0)                  AS cgpa,
    COALESCE(s.percentage, 0.0)            AS percentage,
    COALESCE(s.backlogs, 0)                AS backlogs,
    COALESCE(s.attendance_percentage, 0.0) AS attendance_percentage,
    d.department_name,
    d.department_code,
    p.program_name,
    p.degree_type,
    c.batch_label,
    c.admission_year
  FROM silver.students s
  LEFT JOIN silver.departments      d  ON s.department_id = d.department_id
  LEFT JOIN silver.academic_programs p  ON s.program_id   = p.program_id
  LEFT JOIN silver.cohorts           c  ON s.cohort_id    = c.cohort_id
),
academic AS (
  SELECT
    student_id,
    ROUND(LEAST(100.0, GREATEST(0.0,
      (cgpa / 10.0) * 70.0
      + (percentage / 100.0) * 20.0
      + (attendance_percentage / 100.0) * 10.0
    )), 2) AS academic_score
  FROM base
),
skill_agg AS (
  SELECT
    ss.student_id,
    COUNT(*) AS verified_skill_count,
    ROUND(LEAST(100.0, GREATEST(0.0,
      SUM(ss.proficiency_score * CASE sk.skill_type
            WHEN 'TECHNICAL' THEN 1.0 WHEN 'LANGUAGE' THEN 1.0
            WHEN 'TOOL'      THEN 0.8 WHEN 'DOMAIN'   THEN 0.6
            ELSE 0.5 END)
      / NULLIF(SUM(CASE sk.skill_type
            WHEN 'TECHNICAL' THEN 1.0 WHEN 'LANGUAGE' THEN 1.0
            WHEN 'TOOL'      THEN 0.8 WHEN 'DOMAIN'   THEN 0.6
            ELSE 0.5 END), 0)
    )), 2) AS skill_score,
    ROUND(AVG(CASE WHEN sk.skill_type IN ('TECHNICAL','LANGUAGE','TOOL') THEN ss.proficiency_score END), 2) AS technical_skill_score,
    ROUND(AVG(CASE WHEN sk.skill_type = 'SOFT' THEN ss.proficiency_score END), 2) AS soft_skill_score
  FROM silver.student_skills ss
  JOIN silver.skills sk ON ss.skill_id = sk.skill_id
  GROUP BY ss.student_id
),
internship_agg AS (
  SELECT
    student_id,
    COUNT(*) AS internship_count,
    COALESCE(SUM(duration_months), 0.0) AS internship_months,
    COUNT(CASE WHEN conversion_to_ppo THEN 1 END) AS ppo_count,
    ROUND(LEAST(100.0, GREATEST(0.0,
      LEAST(60.0, COALESCE(SUM(duration_months), 0.0) * 8.0)
      + LEAST(40.0, COUNT(CASE WHEN conversion_to_ppo THEN 1 END) * 20.0)
    )), 2) AS internship_score
  FROM silver.internships
  GROUP BY student_id
),
project_agg AS (
  SELECT
    sp.student_id,
    COUNT(*) AS project_count,
    ROUND(LEAST(100.0, GREATEST(0.0,
      SUM(
        CASE pr.difficulty_level
          WHEN 'EASY'     THEN 10.0
          WHEN 'MEDIUM'   THEN 15.0
          WHEN 'HARD'     THEN 20.0
          WHEN 'RESEARCH' THEN 25.0
          ELSE 12.0
        END
        * (1.0 + COALESCE(pr.industry_relevance_score, 50.0) / 100.0 * 0.5)
        * (CASE WHEN pr.deployed         THEN 1.2 ELSE 1.0 END)
        * (CASE WHEN pr.github_available THEN 1.1 ELSE 1.0 END)
      )
    )), 2) AS project_score
  FROM silver.student_projects sp
  JOIN silver.projects pr ON sp.project_id = pr.project_id
  GROUP BY sp.student_id
),
funnel AS (
  SELECT
    student_id,
    COUNT(*) AS applications_count,
    COUNT(CASE WHEN application_status IN ('SHORTLISTED','INTERVIEW','OFFERED','ACCEPTED') THEN 1 END) AS shortlisted_count,
    COUNT(CASE WHEN application_status IN ('INTERVIEW','OFFERED','ACCEPTED')              THEN 1 END) AS interviews_count,
    COUNT(CASE WHEN application_status IN ('OFFERED','ACCEPTED')                          THEN 1 END) AS offers_count,
    COUNT(CASE WHEN application_status = 'ACCEPTED'                                       THEN 1 END) AS accepted_offers_count
  FROM silver.applications
  GROUP BY student_id
),
interview_perf AS (
  SELECT
    a.student_id,
    COUNT(iv.interview_id) AS total_interview_rounds,
    COUNT(CASE WHEN iv.result = 'PASS' THEN 1 END) AS interview_clears,
    ROUND(COALESCE(AVG(iv.overall_score), 0.0), 2) AS average_interview_score,
    ROUND(COALESCE(MAX(iv.overall_score), 0.0), 2) AS best_interview_score,
    ROUND(LEAST(100.0, GREATEST(0.0, COALESCE(AVG(iv.overall_score), 0.0))), 2) AS interview_score
  FROM silver.interviews iv
  JOIN silver.applications a ON iv.application_id = a.application_id
  GROUP BY a.student_id
),
conversion AS (
  SELECT
    student_id,
    ROUND(LEAST(100.0, GREATEST(0.0,
      CASE WHEN applications_count > 0 THEN
        (
          (shortlisted_count  * 1.0 / applications_count) * 0.5
          + (interviews_count * 1.0 / NULLIF(shortlisted_count, 0)) * 0.5
        ) * 100.0
      ELSE 0.0 END
    )), 2) AS application_conversion_score
  FROM funnel
),
offer_fin AS (
  SELECT
    student_id,
    ROUND(MAX(ctc_lpa), 2) AS highest_offer_lpa,
    ROUND(AVG(ctc_lpa), 2) AS average_offer_lpa,
    ROUND(MAX(CASE WHEN offer_status = 'ACCEPTED' THEN ctc_lpa END), 2) AS accepted_offer_lpa
  FROM silver.offers
  GROUP BY student_id
),
placement_flag AS (
  SELECT student_id, 1 AS placed_flag, MAX(ctc_lpa) AS placed_ctc_lpa
  FROM silver.placements
  WHERE placement_status = 'CONFIRMED'
  GROUP BY student_id
),
cert_agg   AS (SELECT student_id, COUNT(*) AS certification_count FROM silver.student_certifications GROUP BY student_id),
course_agg AS (SELECT student_id, COUNT(*) AS course_count          FROM silver.student_courses       GROUP BY student_id)

SELECT
  b.student_id,
  b.full_name,
  b.gender,
  b.university_roll_no,
  b.cohort_id,
  b.department_id,
  b.department_name,
  b.department_code,
  b.program_id,
  b.program_name,
  b.degree_type,
  b.batch_label,
  b.admission_year,
  b.graduation_year,
  b.current_semester,
  b.placement_status,
  b.preferred_role,
  b.preferred_location,
  b.work_authorization,
  b.cgpa,
  b.percentage,
  b.backlogs,
  b.attendance_percentage,

  -- Component Scores (0-100)
  ac.academic_score,
  COALESCE(sk.skill_score, 0.0) AS skill_score,
  COALESCE(ia.internship_score, 0.0) AS internship_score,
  COALESCE(pa.project_score, 0.0) AS project_score,
  COALESCE(ip.interview_score, 0.0) AS interview_score,
  COALESCE(cv.application_conversion_score, 0.0) AS application_conversion_score,

  -- Placement Readiness Score (Weighted)
  ROUND(
    ac.academic_score * 0.20
    + COALESCE(sk.skill_score, 0.0) * 0.25
    + COALESCE(ia.internship_score, 0.0) * 0.10
    + COALESCE(pa.project_score, 0.0) * 0.10
    + COALESCE(ip.interview_score, 0.0) * 0.20
    + COALESCE(cv.application_conversion_score, 0.0) * 0.15
  , 2) AS placement_readiness_score,

  COALESCE(sk.verified_skill_count, 0) AS verified_skill_count,
  sk.technical_skill_score,
  sk.soft_skill_score,
  COALESCE(ia.internship_count, 0) AS internship_count,
  COALESCE(ia.internship_months, 0.0) AS internship_months,
  COALESCE(ia.ppo_count, 0) AS ppo_count,
  COALESCE(pa.project_count, 0) AS project_count,
  COALESCE(f.applications_count, 0) AS applications_count,
  COALESCE(f.shortlisted_count, 0) AS shortlisted_count,
  COALESCE(f.interviews_count, 0) AS interviews_count,
  COALESCE(f.offers_count, 0) AS offers_count,
  COALESCE(f.accepted_offers_count, 0) AS accepted_offers_count,
  COALESCE(ip.total_interview_rounds, 0) AS total_interview_rounds,
  COALESCE(ip.interview_clears, 0) AS interview_clears,
  COALESCE(ip.average_interview_score, 0.0) AS average_interview_score,
  COALESCE(ip.best_interview_score, 0.0) AS best_interview_score,

  -- Conversion rates
  CASE WHEN COALESCE(f.applications_count,0) > 0 THEN ROUND(f.shortlisted_count * 100.0 / f.applications_count, 2) END AS application_to_shortlist_rate,
  CASE WHEN COALESCE(f.shortlisted_count,0) > 0 THEN ROUND(f.interviews_count * 100.0 / f.shortlisted_count, 2) END AS shortlist_to_interview_rate,
  CASE WHEN COALESCE(f.interviews_count,0) > 0 THEN ROUND(f.offers_count * 100.0 / f.interviews_count, 2) END AS interview_to_offer_rate,
  CASE WHEN COALESCE(f.applications_count,0) > 0 THEN ROUND(f.offers_count * 100.0 / f.applications_count, 2) END AS application_to_offer_rate,
  CASE WHEN COALESCE(f.offers_count,0) > 0 THEN ROUND(f.accepted_offers_count * 100.0 / f.offers_count, 2) END AS offer_acceptance_rate,

  of_fin.highest_offer_lpa,
  of_fin.average_offer_lpa,
  of_fin.accepted_offer_lpa,

  COALESCE(pf.placed_flag, 0) AS placed_flag,
  pf.placed_ctc_lpa,
  COALESCE(ca.certification_count, 0) AS certification_count,
  COALESCE(co.course_count, 0) AS course_count,

  CASE WHEN ac.academic_score >= 75 AND COALESCE(ip.interview_score,0) < 50 THEN TRUE ELSE FALSE END AS strong_academic_weak_interview_flag,
  CASE WHEN b.placement_status IN ('ELIGIBLE','ACTIVE') AND COALESCE(pf.placed_flag,0) = 0 THEN TRUE ELSE FALSE END AS unplaced_eligible_flag,
  current_timestamp AS profile_computed_at

FROM base b
LEFT JOIN academic ac ON b.student_id = ac.student_id
LEFT JOIN skill_agg sk ON b.student_id = sk.student_id
LEFT JOIN internship_agg ia ON b.student_id = ia.student_id
LEFT JOIN project_agg pa ON b.student_id = pa.student_id
LEFT JOIN funnel f ON b.student_id = f.student_id
LEFT JOIN interview_perf ip ON b.student_id = ip.student_id
LEFT JOIN conversion cv ON b.student_id = cv.student_id
LEFT JOIN offer_fin of_fin ON b.student_id = of_fin.student_id
LEFT JOIN placement_flag pf ON b.student_id = pf.student_id
LEFT JOIN cert_agg ca ON b.student_id = ca.student_id
LEFT JOIN course_agg co ON b.student_id = co.student_id;
""")
print("  ✓ Created gold.student_placement_profile (50,000 student profiles)")

# B. Company Hiring Profile (Independent CTEs to eliminate 1-to-many multiplication)
con.execute("""
CREATE OR REPLACE TABLE gold.company_hiring_profile AS
WITH job_postings_agg AS (
    SELECT company_id,
           COUNT(DISTINCT job_posting_id) AS job_postings_count,
           SUM(openings) AS openings_count
    FROM silver.job_postings
    GROUP BY company_id
),
applications_agg AS (
    SELECT jp.company_id,
           COUNT(DISTINCT a.application_id) AS applications_count,
           COUNT(DISTINCT CASE WHEN ash.status IN ('SHORTLISTED','INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) AS shortlisted_count,
           COUNT(DISTINCT CASE WHEN ash.status IN ('INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) AS interviews_count
    FROM silver.applications a
    JOIN silver.job_postings jp ON a.job_posting_id = jp.job_posting_id
    LEFT JOIN silver.application_status_history ash ON a.application_id = ash.application_id
    GROUP BY jp.company_id
),
interviews_agg AS (
    SELECT jp.company_id,
           AVG(iv.overall_score) AS average_interview_score
    FROM silver.interviews iv
    JOIN silver.applications a ON iv.application_id = a.application_id
    JOIN silver.job_postings jp ON a.job_posting_id = jp.job_posting_id
    GROUP BY jp.company_id
),
offers_agg AS (
    SELECT jp.company_id,
           COUNT(DISTINCT o.offer_id) AS offers_count,
           COUNT(DISTINCT CASE WHEN o.offer_status = 'ACCEPTED' THEN o.offer_id END) AS accepted_offers_count
    FROM silver.offers o
    JOIN silver.applications a ON o.application_id = a.application_id
    JOIN silver.job_postings jp ON a.job_posting_id = jp.job_posting_id
    GROUP BY jp.company_id
),
placements_agg AS (
    SELECT jp.company_id,
           COUNT(DISTINCT p.placement_id) AS placements_count,
           ROUND(AVG(p.ctc_lpa), 2) AS average_ctc_lpa,
           ROUND(MEDIAN(p.ctc_lpa), 2) AS median_ctc_lpa,
           ROUND(MAX(p.ctc_lpa), 2) AS highest_ctc_lpa,
           ROUND(MIN(p.ctc_lpa), 2) AS lowest_ctc_lpa
    FROM silver.placements p
    JOIN silver.offers o ON p.offer_id = o.offer_id
    JOIN silver.applications a ON o.application_id = a.application_id
    JOIN silver.job_postings jp ON a.job_posting_id = jp.job_posting_id
    GROUP BY jp.company_id
)
SELECT
    c.company_id,
    c.company_name,
    c.industry,
    c.company_type,
    CASE WHEN c.is_product_company THEN 'PRODUCT' WHEN c.is_service_company THEN 'SERVICES' ELSE 'OTHER' END AS product_or_service,
    COALESCE(jpa.job_postings_count, 0) AS job_postings_count,
    COALESCE(jpa.openings_count, 0) AS openings_count,
    COALESCE(aa.applications_count, 0) AS applications_count,
    COALESCE(aa.shortlisted_count, 0) AS shortlisted_count,
    COALESCE(aa.interviews_count, 0) AS interviews_count,
    COALESCE(oa.offers_count, 0) AS offers_count,
    COALESCE(oa.accepted_offers_count, 0) AS accepted_offers_count,
    COALESCE(pa.placements_count, 0) AS placements_count,
    pa.average_ctc_lpa,
    pa.median_ctc_lpa,
    pa.highest_ctc_lpa,
    pa.lowest_ctc_lpa,
    CASE WHEN COALESCE(aa.applications_count, 0) > 0 THEN ROUND(COALESCE(aa.interviews_count, 0) * 100.0 / aa.applications_count, 2) END AS application_to_interview_rate,
    CASE WHEN COALESCE(aa.interviews_count, 0) > 0 THEN ROUND(COALESCE(oa.offers_count, 0) * 100.0 / aa.interviews_count, 2) END AS interview_to_offer_rate,
    CASE WHEN COALESCE(oa.offers_count, 0) > 0 THEN ROUND(COALESCE(oa.accepted_offers_count, 0) * 100.0 / oa.offers_count, 2) END AS offer_acceptance_rate,
    CASE WHEN COALESCE(aa.applications_count, 0) > 0 THEN ROUND(COALESCE(pa.placements_count, 0) * 100.0 / aa.applications_count, 2) END AS application_to_placement_rate,
    ROUND(ia.average_interview_score, 2) AS average_interview_score
FROM silver.companies c
LEFT JOIN job_postings_agg jpa ON c.company_id = jpa.company_id
LEFT JOIN applications_agg aa ON c.company_id = aa.company_id
LEFT JOIN interviews_agg ia ON c.company_id = ia.company_id
LEFT JOIN offers_agg oa ON c.company_id = oa.company_id
LEFT JOIN placements_agg pa ON c.company_id = pa.company_id;
""")
print("  ✓ Created gold.company_hiring_profile")

# C. Department Placement Performance
con.execute("""
CREATE OR REPLACE TABLE gold.department_placement_performance AS
SELECT
    d.department_code,
    d.department_name,
    s.graduation_year,
    COUNT(DISTINCT s.student_id) AS total_students,
    COUNT(DISTINCT CASE WHEN s.placement_status IN ('ELIGIBLE','ACTIVE','PLACED') THEN s.student_id END) AS eligible_students,
    COUNT(DISTINCT CASE WHEN s.placement_status = 'PLACED' OR p.placement_id IS NOT NULL THEN s.student_id END) AS placed_students,
    ROUND(COUNT(DISTINCT CASE WHEN s.placement_status = 'PLACED' OR p.placement_id IS NOT NULL THEN s.student_id END) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN s.placement_status IN ('ELIGIBLE','ACTIVE','PLACED') THEN s.student_id END), 0), 2) AS placement_rate,
    ROUND(AVG(p.ctc_lpa), 2) AS average_ctc_lpa,
    ROUND(MEDIAN(p.ctc_lpa), 2) AS median_ctc_lpa,
    ROUND(MAX(p.ctc_lpa), 2) AS highest_ctc_lpa
FROM silver.departments d
JOIN silver.students s ON d.department_id = s.department_id
LEFT JOIN silver.placements p ON s.student_id = p.student_id
GROUP BY d.department_code, d.department_name, s.graduation_year;
""")
print("  ✓ Created gold.department_placement_performance")

# D. Skill Demand Profile (Isolated Demand & Supply CTEs)
con.execute("""
CREATE OR REPLACE TABLE gold.skill_demand_profile AS
WITH market_demand AS (
    SELECT
        jrs.skill_id,
        COUNT(DISTINCT jrs.job_posting_id) AS job_posting_count,
        COUNT(DISTINCT jp.company_id) AS company_count,
        COALESCE(SUM(jp.openings), 0) AS total_openings,
        AVG(jrs.required_score) AS average_required_score
    FROM silver.job_required_skills jrs
    JOIN silver.job_postings jp ON jrs.job_posting_id = jp.job_posting_id
    GROUP BY jrs.skill_id
),
student_supply AS (
    SELECT
        ss.skill_id,
        COUNT(DISTINCT ss.student_id) AS students_with_skill_count,
        AVG(ss.proficiency_score) AS average_student_proficiency
    FROM silver.student_skills ss
    GROUP BY ss.skill_id
)
SELECT
    sk.skill_id,
    sk.skill_name,
    sk.skill_category,
    sk.skill_type,
    COALESCE(md.job_posting_count, 0) AS job_posting_count,
    COALESCE(md.company_count, 0) AS company_count,
    COALESCE(md.total_openings, 0) AS total_openings,
    COALESCE(ss.students_with_skill_count, 0) AS students_with_skill_count,
    ROUND(md.average_required_score, 2) AS average_required_score,
    ROUND(ss.average_student_proficiency, 2) AS average_student_proficiency,
    ROUND(COALESCE(md.average_required_score, 0) - COALESCE(ss.average_student_proficiency, 0), 2) AS average_skill_gap,
    DENSE_RANK() OVER (ORDER BY COALESCE(md.job_posting_count, 0) DESC) AS demand_rank
FROM silver.skills sk
LEFT JOIN market_demand md ON sk.skill_id = md.skill_id
LEFT JOIN student_supply ss ON sk.skill_id = ss.skill_id;
""")
print("  ✓ Created gold.skill_demand_profile")

# E. Student Job Skill Match
con.execute("""
CREATE OR REPLACE TABLE gold.student_job_skill_match AS
SELECT 
    ss.student_id, jrs.job_posting_id,
    SUM(jrs.importance_weight * GREATEST(0, jrs.required_score - COALESCE(ss.student_score, 0))) / NULLIF(SUM(jrs.importance_weight * jrs.required_score), 0) AS weighted_deficit,
    100 - (SUM(jrs.importance_weight * GREATEST(0, jrs.required_score - COALESCE(ss.student_score, 0))) / NULLIF(SUM(jrs.importance_weight * jrs.required_score), 0) * 100) AS skill_match_percentage,
    SUM(CASE WHEN jrs.is_mandatory AND ss.student_score IS NULL THEN 1 ELSE 0 END) AS missing_mandatory_skill_count
FROM silver.job_required_skills jrs
CROSS JOIN (SELECT DISTINCT student_id FROM silver.students) st
LEFT JOIN (SELECT student_id, skill_id, proficiency_score as student_score FROM silver.student_skills) ss 
  ON st.student_id = ss.student_id AND jrs.skill_id = ss.skill_id
GROUP BY ss.student_id, jrs.job_posting_id;
""")
print("  ✓ Created gold.student_job_skill_match")

# 4. Authoritative Semantic Layer Views (Five Curated Genie Objects)
print("\n[4/4] Creating Five Authoritative Genie Semantic Views...")

con.execute("""
CREATE OR REPLACE VIEW semantic.genie_student_intelligence AS
SELECT 
    s.student_id,
    s.full_name,
    s.gender,
    s.university_roll_no,
    s.cohort_id,
    s.department_id,
    s.department_name,
    s.department_code,
    s.program_id,
    s.program_name,
    s.degree_type,
    s.batch_label,
    s.admission_year,
    s.graduation_year,
    s.current_semester,
    s.placement_status,
    s.preferred_role,
    s.preferred_location,
    s.work_authorization,
    s.cgpa,
    s.percentage,
    s.backlogs,
    s.attendance_percentage,

    -- Governed Component Scores (0-100)
    s.academic_score,
    s.skill_score,
    s.internship_score,
    s.project_score,
    s.interview_score,
    s.application_conversion_score,

    -- Placement Readiness Score (Weighted 0-100 index)
    s.placement_readiness_score,

    -- Governed Categorical Readiness Band
    CASE 
        WHEN s.placement_readiness_score >= 90.0 THEN 'VERY_HIGH'
        WHEN s.placement_readiness_score >= 75.0 THEN 'HIGH'
        WHEN s.placement_readiness_score >= 60.0 THEN 'MODERATE'
        WHEN s.placement_readiness_score >= 40.0 THEN 'LOW'
        ELSE 'VERY_LOW'
    END AS readiness_band,

    -- Governed Placement Stage
    CASE 
        WHEN s.placed_flag = 1 THEN 'PLACED'
        WHEN s.accepted_offers_count > 0 THEN 'OFFER_ACCEPTED'
        WHEN s.offers_count > 0 THEN 'OFFERED'
        WHEN s.placement_status = 'ACTIVE' THEN 'ACTIVE'
        WHEN s.placement_status = 'OPTED_OUT' THEN 'OPTED_OUT'
        WHEN s.placement_status = 'ELIGIBLE' THEN 'ELIGIBLE'
        ELSE 'NOT_STARTED'
    END AS placement_outcome_stage,

    -- Experience & Alignment Scores
    ROUND(LEAST(100.0, GREATEST(0.0, s.internship_score * 0.70 + s.project_score * 0.30)), 2) AS experience_strength_score,
    ROUND(LEAST(100.0, GREATEST(0.0, s.skill_score * 0.50 + s.project_score * 0.30 + s.internship_score * 0.20)), 2) AS career_alignment_score,

    -- Activity & Offer Quality
    CASE
        WHEN s.applications_count >= 15 THEN 'VERY_HIGH'
        WHEN s.applications_count >= 8  THEN 'HIGH'
        WHEN s.applications_count >= 4  THEN 'MODERATE'
        WHEN s.applications_count >= 1  THEN 'LOW'
        ELSE 'NONE'
    END AS application_activity_level,

    CASE
        WHEN s.highest_offer_lpa >= 20.0 THEN 'PREMIUM'
        WHEN s.highest_offer_lpa >= 12.0 THEN 'HIGH'
        WHEN s.highest_offer_lpa >= 6.0  THEN 'MID'
        WHEN s.highest_offer_lpa > 0.0   THEN 'ENTRY'
        ELSE 'NO_OFFER'
    END AS offer_quality_band,

    -- Readiness Confidence (Data Completeness)
    CASE 
        WHEN s.total_interview_rounds >= 2 AND s.verified_skill_count >= 5 THEN 'HIGH'
        WHEN s.total_interview_rounds >= 1 OR s.verified_skill_count >= 3 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS placement_readiness_confidence,

    -- Skill & Experience Details
    s.verified_skill_count,
    s.technical_skill_score,
    s.soft_skill_score,
    s.internship_count,
    s.internship_months,
    s.ppo_count,
    s.project_count,
    s.certification_count,
    s.course_count,

    -- Funnel Counts & Conversion Rates
    s.applications_count,
    s.shortlisted_count,
    s.interviews_count,
    s.offers_count,
    s.accepted_offers_count,
    s.total_interview_rounds,
    s.interview_clears,
    s.average_interview_score,
    s.best_interview_score,
    s.application_to_shortlist_rate,
    s.shortlist_to_interview_rate,
    s.interview_to_offer_rate,
    s.application_to_offer_rate,
    s.offer_acceptance_rate,

    -- Financials & Outcomes
    s.highest_offer_lpa,
    s.average_offer_lpa,
    s.accepted_offer_lpa,
    s.placed_flag,
    s.placed_ctc_lpa,

    -- Diagnostic Indicators
    s.strong_academic_weak_interview_flag,
    s.unplaced_eligible_flag,
    s.profile_computed_at

FROM gold.student_placement_profile s;

CREATE OR REPLACE VIEW semantic.genie_company_intelligence AS
SELECT 
    c.company_id,
    c.company_name,
    c.industry,
    c.company_type,
    c.product_or_service,
    c.job_postings_count,
    c.openings_count,
    c.applications_count,
    c.shortlisted_count,
    c.interviews_count,
    c.offers_count,
    c.accepted_offers_count,
    c.placements_count,
    c.average_ctc_lpa,
    c.median_ctc_lpa,
    c.highest_ctc_lpa,
    c.lowest_ctc_lpa,
    c.application_to_interview_rate,
    c.interview_to_offer_rate,
    c.offer_acceptance_rate,
    c.application_to_placement_rate,
    c.average_interview_score,

    -- Selectivity & Conversion Index
    CASE WHEN c.applications_count > 0 
         THEN ROUND(100.0 - (c.offers_count * 100.0 / c.applications_count), 2)
         ELSE 50.0 
    END AS hiring_selectivity_score,

    CASE WHEN c.applications_count > 0 
         THEN ROUND((c.placements_count * 100.0 / c.applications_count), 2)
         ELSE 0.0 
    END AS hiring_conversion_score,

    -- Package Position
    CASE 
        WHEN c.average_ctc_lpa >= 15.0 THEN 'TOP_DECILE'
        WHEN c.average_ctc_lpa >= 8.0  THEN 'ABOVE_MEDIAN'
        WHEN c.average_ctc_lpa >= 5.0  THEN 'AROUND_MEDIAN'
        WHEN c.average_ctc_lpa > 0.0   THEN 'BELOW_MEDIAN'
        ELSE 'NOT_AVAILABLE'
    END AS company_package_position

FROM gold.company_hiring_profile c;

CREATE OR REPLACE VIEW semantic.genie_department_performance AS
WITH base AS (
    SELECT 
        d.department_code,
        d.department_name,
        d.graduation_year,
        d.total_students,
        d.eligible_students,
        d.placed_students,
        d.placement_rate,
        d.average_ctc_lpa,
        d.median_ctc_lpa,
        d.highest_ctc_lpa,
        LAG(d.placement_rate) OVER(PARTITION BY d.department_code ORDER BY d.graduation_year) AS prev_placement_rate,
        LAG(d.average_ctc_lpa) OVER(PARTITION BY d.department_code ORDER BY d.graduation_year) AS prev_average_ctc
    FROM gold.department_placement_performance d
)
SELECT 
    department_code,
    department_name,
    graduation_year,
    total_students,
    eligible_students,
    placed_students,
    placement_rate,
    average_ctc_lpa,
    median_ctc_lpa,
    highest_ctc_lpa,
    prev_placement_rate AS placement_rate_yoy,
    ROUND(placement_rate - COALESCE(prev_placement_rate, placement_rate), 2) AS placement_rate_change_points,
    prev_average_ctc AS average_ctc_yoy,
    DENSE_RANK() OVER(PARTITION BY graduation_year ORDER BY placement_rate DESC) AS rank_within_year
FROM base;

CREATE OR REPLACE VIEW semantic.genie_skill_market AS
WITH totals AS (
    SELECT 
        (SELECT COUNT(*) FROM silver.job_postings) AS total_jobs,
        (SELECT COUNT(*) FROM silver.students WHERE placement_status IN ('ELIGIBLE','ACTIVE','PLACED')) AS total_eligible_students
)
SELECT 
    sk.skill_id,
    sk.skill_name,
    sk.skill_category,
    sk.skill_type,
    sk.job_posting_count,
    sk.company_count,
    sk.total_openings,
    sk.students_with_skill_count,
    sk.average_required_score,
    sk.average_student_proficiency,
    sk.average_skill_gap,
    sk.demand_rank,
    ROUND(sk.students_with_skill_count * 1.0 / t.total_eligible_students, 4) AS student_supply_ratio,
    ROUND(sk.job_posting_count * 1.0 / t.total_jobs, 4) AS market_demand_ratio,
    ROUND((sk.job_posting_count * 1.0 / t.total_jobs) - (sk.students_with_skill_count * 1.0 / t.total_eligible_students), 4) AS skill_supply_demand_gap,
    CASE 
        WHEN (sk.job_posting_count * 1.0 / t.total_jobs) > 0.15 
         AND (sk.students_with_skill_count * 1.0 / t.total_eligible_students) < 0.35 
        THEN TRUE ELSE FALSE 
    END AS high_demand_low_supply_flag
FROM gold.skill_demand_profile sk
CROSS JOIN totals t;

CREATE OR REPLACE VIEW semantic.genie_student_job_match AS
SELECT 
    m.student_id,
    m.job_posting_id,
    m.weighted_deficit,
    m.skill_match_percentage,
    ROUND(100.0 - m.skill_match_percentage, 2) AS skill_gap_percentage,
    m.missing_mandatory_skill_count,
    ROUND(LEAST(100.0, GREATEST(0.0, m.skill_match_percentage * 0.40 + 60.0 * 0.60)), 2) AS ranking_score,
    CASE 
        WHEN m.skill_match_percentage >= 85.0 THEN 'EXCELLENT'
        WHEN m.skill_match_percentage >= 70.0 THEN 'STRONG'
        WHEN m.skill_match_percentage >= 50.0 THEN 'GOOD'
        WHEN m.skill_match_percentage >= 35.0 THEN 'FAIR'
        ELSE 'POOR'
    END AS candidate_fit_band
FROM gold.student_job_skill_match m;
""")
print("  ✓ Created five authoritative semantic Genie views in placewise.semantic")

elapsed = time.time() - start_time
print(f"\n=======================================================")
print(f" DATABASE REBUILD COMPLETE in {elapsed:.2f} seconds!")
print(f" DuckDB File: {DB_FILE} ({os.path.getsize(DB_FILE) / (1024*1024):.2f} MB)")
print(f"=======================================================\n")
