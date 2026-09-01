CREATE OR REPLACE TABLE placewise.gold.student_application_funnel AS
SELECT 
    student_id,
    COUNT(id) AS applications_count,
    SUM(CASE WHEN application_status = 'SHORTLISTED' THEN 1 ELSE 0 END) AS shortlisted_count,
    CASE WHEN COUNT(id) > 0 THEN ROUND(SUM(CASE WHEN application_status = 'SHORTLISTED' THEN 1 ELSE 0 END) * 100.0 / COUNT(id), 2) ELSE NULL END AS application_to_shortlist_rate
FROM placewise.silver.applications
GROUP BY student_id;\n