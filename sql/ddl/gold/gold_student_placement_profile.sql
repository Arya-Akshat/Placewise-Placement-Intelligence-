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
LEFT JOIN (SELECT student_id, CASE WHEN COUNT(id) > 0 THEN ROUND(SUM(CASE WHEN application_status = 'SHORTLISTED' THEN 1 ELSE 0 END) * 100.0 / COUNT(id), 2) ELSE 0 END as application_conversion_score FROM placewise.silver.applications GROUP BY student_id) ac ON s.student_id = ac.student_id;\n