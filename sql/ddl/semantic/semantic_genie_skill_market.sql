-- =============================================================================
-- PLACEWISE: Authoritative Genie Semantic View — Skill Market
-- Schema: placewise.semantic
-- Grain:  One row per skill
-- =============================================================================

CREATE OR REPLACE VIEW placewise.semantic.genie_skill_market AS
WITH totals AS (
    SELECT 
        (SELECT COUNT(*) FROM placewise.silver.job_postings) AS total_jobs,
        (SELECT COUNT(*) FROM placewise.silver.students WHERE placement_status IN ('ELIGIBLE','ACTIVE','PLACED')) AS total_eligible_students
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
FROM placewise.gold.skill_demand_profile sk
CROSS JOIN totals t;
