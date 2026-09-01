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
GROUP BY ss.student_id, jrs.job_posting_id;\n