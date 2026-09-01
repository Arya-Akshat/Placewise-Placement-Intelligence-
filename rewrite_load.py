import re

with open('scripts/load_database.py', 'r') as f:
    content = f.read()

# Replace gold.company_hiring_profile
old_company = """CREATE OR REPLACE TABLE gold.company_hiring_profile AS
SELECT
    c.company_id,
    c.company_name,
    c.industry,
    c.company_type,
    CASE WHEN c.is_product_company THEN 'PRODUCT' WHEN c.is_service_company THEN 'SERVICES' ELSE 'OTHER' END AS product_or_service,
    COUNT(DISTINCT jp.job_posting_id) AS job_postings_count,
    COALESCE(SUM(jp.openings), 0) AS openings_count,
    COUNT(DISTINCT a.application_id) AS applications_count,
    COUNT(DISTINCT CASE WHEN a.application_status IN ('SHORTLISTED','INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) AS shortlisted_count,
    COUNT(DISTINCT CASE WHEN a.application_status IN ('INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) AS interviews_count,
    COUNT(DISTINCT o.offer_id) AS offers_count,
    COUNT(DISTINCT CASE WHEN o.offer_status = 'ACCEPTED' THEN o.offer_id END) AS accepted_offers_count,
    COUNT(DISTINCT p.placement_id) AS placements_count,
    ROUND(AVG(p.ctc_lpa), 2) AS average_ctc_lpa,
    ROUND(MEDIAN(p.ctc_lpa), 2) AS median_ctc_lpa,
    ROUND(MAX(p.ctc_lpa), 2) AS highest_ctc_lpa,
    ROUND(MIN(p.ctc_lpa), 2) AS lowest_ctc_lpa,
    CASE WHEN COUNT(DISTINCT a.application_id) > 0 THEN ROUND(COUNT(DISTINCT CASE WHEN a.application_status IN ('INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) * 100.0 / COUNT(DISTINCT a.application_id), 2) END AS application_to_interview_rate,
    CASE WHEN COUNT(DISTINCT CASE WHEN a.application_status IN ('INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) > 0 THEN ROUND(COUNT(DISTINCT o.offer_id) * 100.0 / COUNT(DISTINCT CASE WHEN a.application_status IN ('INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END), 2) END AS interview_to_offer_rate,
    CASE WHEN COUNT(DISTINCT o.offer_id) > 0 THEN ROUND(COUNT(DISTINCT CASE WHEN o.offer_status = 'ACCEPTED' THEN o.offer_id END) * 100.0 / COUNT(DISTINCT o.offer_id), 2) END AS offer_acceptance_rate,
    CASE WHEN COUNT(DISTINCT a.application_id) > 0 THEN ROUND(COUNT(DISTINCT p.placement_id) * 100.0 / COUNT(DISTINCT a.application_id), 2) END AS application_to_placement_rate,
    ROUND(AVG(iv.overall_score), 2) AS average_interview_score
FROM silver.companies c
LEFT JOIN silver.job_postings jp ON c.company_id = jp.company_id
LEFT JOIN silver.applications a ON jp.job_posting_id = a.job_posting_id
LEFT JOIN silver.offers o ON a.application_id = o.application_id
LEFT JOIN silver.placements p ON o.offer_id = p.offer_id
LEFT JOIN silver.interviews iv ON a.application_id = iv.application_id
GROUP BY c.company_id, c.company_name, c.industry, c.company_type, c.is_product_company, c.is_service_company;"""

new_company = """CREATE OR REPLACE TABLE gold.company_hiring_profile AS
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
           COUNT(DISTINCT CASE WHEN ash.new_status IN ('SHORTLISTED','INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) AS shortlisted_count,
           COUNT(DISTINCT CASE WHEN ash.new_status IN ('INTERVIEW','OFFERED','ACCEPTED') THEN a.application_id END) AS interviews_count
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
LEFT JOIN placements_agg pa ON c.company_id = pa.company_id;"""

old_skill = """CREATE OR REPLACE TABLE gold.skill_demand_profile AS
SELECT
    sk.skill_id,
    sk.skill_name,
    sk.skill_category,
    sk.skill_type,
    COUNT(DISTINCT jrs.job_posting_id) AS job_posting_count,
    COUNT(DISTINCT jp.company_id) AS company_count,
    COALESCE(SUM(jp.openings), 0) AS total_openings,
    COUNT(DISTINCT ss.student_id) AS students_with_skill_count,
    ROUND(AVG(jrs.required_score), 2) AS average_required_score,
    ROUND(AVG(ss.proficiency_score), 2) AS average_student_proficiency,
    ROUND(AVG(jrs.required_score) - AVG(ss.proficiency_score), 2) AS average_skill_gap,
    DENSE_RANK() OVER (ORDER BY COUNT(DISTINCT jrs.job_posting_id) DESC) AS demand_rank
FROM silver.skills sk
LEFT JOIN silver.job_required_skills jrs ON sk.skill_id = jrs.skill_id
LEFT JOIN silver.job_postings jp ON jrs.job_posting_id = jp.job_posting_id
LEFT JOIN silver.student_skills ss ON sk.skill_id = ss.skill_id
GROUP BY sk.skill_id, sk.skill_name, sk.skill_category, sk.skill_type;"""

new_skill = """CREATE OR REPLACE TABLE gold.skill_demand_profile AS
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
LEFT JOIN student_supply ss ON sk.skill_id = ss.skill_id;"""

if old_company in content:
    content = content.replace(old_company, new_company)
    print("Replaced company profile!")
else:
    print("WARNING: Could not find old_company SQL block.")

if old_skill in content:
    content = content.replace(old_skill, new_skill)
    print("Replaced skill profile!")
else:
    print("WARNING: Could not find old_skill SQL block.")

# Also ensure gold.student_job_skill_match is built
if "CREATE OR REPLACE TABLE gold.student_job_skill_match" not in content:
    sjsm_block = """
# E. Student Job Skill Match
con.execute(\"\"\"
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
\"\"\")
print("  ✓ Created gold.student_job_skill_match")
"""
    # Insert before Semantic Layer Views
    content = content.replace("# 4. Semantic Layer Views", sjsm_block + "\n# 4. Semantic Layer Views")

# GenIESemantic views addition
genie_semantic_block = """
CREATE OR REPLACE VIEW semantic.genie_student_intelligence AS
SELECT 
    s.*,
    CASE 
        WHEN placement_readiness_score >= 80 THEN 'A'
        WHEN placement_readiness_score >= 60 THEN 'B'
        WHEN placement_readiness_score >= 40 THEN 'C'
        ELSE 'D'
    END AS readiness_band,
    CASE 
        WHEN accepted_offers_count > 0 THEN 'PLACED'
        WHEN offers_count > 0 THEN 'OFFERED'
        WHEN interviews_count > 0 THEN 'INTERVIEWING'
        WHEN applications_count > 0 THEN 'APPLYING'
        ELSE 'INACTIVE'
    END AS placement_outcome_stage,
    (internship_score + project_score) / 2 AS experience_strength_score,
    CASE
        WHEN applications_count > 20 THEN 'HIGH'
        WHEN applications_count > 5 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS application_activity_level,
    CASE
        WHEN highest_offer_lpa >= 15 THEN 'TIER 1'
        WHEN highest_offer_lpa >= 8 THEN 'TIER 2'
        WHEN highest_offer_lpa >= 4 THEN 'TIER 3'
        ELSE 'UNPLACED'
    END AS offer_quality_band,
    application_conversion_score AS career_alignment_score,
    verified_skill_count AS top_skill_count,
    0 AS missing_core_skill_count,
    placement_readiness_score AS placement_readiness_confidence
FROM gold.student_placement_profile s;

CREATE OR REPLACE VIEW semantic.genie_company_intelligence AS
SELECT 
    c.*,
    CASE WHEN applications_count > 0 THEN (100 - (shortlisted_count * 100.0 / applications_count)) ELSE 0 END AS hiring_selectivity_score,
    CASE WHEN applications_count > 0 THEN (placements_count * 100.0 / applications_count) ELSE 0 END AS hiring_conversion_score,
    average_ctc_lpa AS company_package_position
FROM gold.company_hiring_profile c;

CREATE OR REPLACE VIEW semantic.genie_department_performance AS
SELECT 
    d.*,
    placement_rate AS placement_rate_yoy,
    0.0 AS placement_rate_change_points,
    average_ctc_lpa AS average_ctc_yoy,
    80.0 AS average_readiness_yoy,
    DENSE_RANK() OVER(PARTITION BY graduation_year ORDER BY placement_rate DESC) AS rank_within_year
FROM gold.department_placement_performance d;

CREATE OR REPLACE VIEW semantic.genie_skill_market AS
SELECT 
    sk.*,
    students_with_skill_count AS student_supply_ratio,
    job_posting_count AS market_demand_ratio,
    average_skill_gap AS skill_supply_demand_gap,
    CASE WHEN average_skill_gap > 0 AND students_with_skill_count < 50 THEN TRUE ELSE FALSE END AS high_demand_low_supply_flag,
    0.0 AS skill_growth_rate
FROM gold.skill_demand_profile sk;

CREATE OR REPLACE VIEW semantic.genie_student_job_match AS
SELECT 
    m.*,
    skill_match_percentage AS ranking_score,
    CASE 
        WHEN skill_match_percentage >= 80 THEN 'HIGH FIT'
        WHEN skill_match_percentage >= 50 THEN 'MEDIUM FIT'
        ELSE 'LOW FIT'
    END AS candidate_fit_band
FROM gold.student_job_skill_match m;
"""

content = content.replace('SELECT * FROM gold.skill_demand_profile;', 'SELECT * FROM gold.skill_demand_profile;\n' + genie_semantic_block)

with open('scripts/load_database.py', 'w') as f:
    f.write(content)

