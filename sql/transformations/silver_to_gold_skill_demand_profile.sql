CREATE OR REPLACE TABLE placewise.gold.skill_demand_profile AS
WITH market_demand AS (
    SELECT
        jrs.skill_id,
        COUNT(DISTINCT jrs.job_posting_id) AS job_posting_count,
        COUNT(DISTINCT jp.company_id) AS company_count,
        COALESCE(SUM(jp.openings), 0) AS total_openings,
        AVG(jrs.required_score) AS average_required_score
    FROM placewise.silver.job_required_skills jrs
    JOIN placewise.silver.job_postings jp ON jrs.job_posting_id = jp.job_posting_id
    GROUP BY jrs.skill_id
),
student_supply AS (
    SELECT
        ss.skill_id,
        COUNT(DISTINCT ss.student_id) AS students_with_skill_count,
        AVG(ss.proficiency_score) AS average_student_proficiency
    FROM placewise.silver.student_skills ss
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
FROM placewise.silver.skills sk
LEFT JOIN market_demand md ON sk.skill_id = md.skill_id
LEFT JOIN student_supply ss ON sk.skill_id = ss.skill_id;
