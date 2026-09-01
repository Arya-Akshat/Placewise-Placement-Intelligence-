-- Check 1: student_fk exists
SELECT 'student_fk' AS check_name,
       COUNT(*) FILTER (WHERE student_id NOT IN (SELECT student_id FROM placewise.silver.students)) AS failed_count,
       COUNT(*) AS total_count,
       'CRITICAL' AS severity
FROM placewise.silver.applications;

-- Check 2: posting_fk exists
SELECT 'posting_fk' AS check_name,
       COUNT(*) FILTER (WHERE job_posting_id NOT IN (SELECT job_posting_id FROM placewise.silver.job_postings)) AS failed_count,
       COUNT(*) AS total_count,
       'CRITICAL' AS severity
FROM placewise.silver.applications;
