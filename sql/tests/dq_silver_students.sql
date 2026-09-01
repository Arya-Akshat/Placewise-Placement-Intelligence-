-- Check 1: CGPA range
SELECT 'cgpa_range' AS check_name,
       COUNT(*) FILTER (WHERE cgpa NOT BETWEEN 0 AND 10) AS failed_count,
       COUNT(*) AS total_count,
       'CRITICAL' AS severity
FROM placewise.silver.students;

-- Check 2: Unique student_id
SELECT 'student_id_unique' AS check_name,
       COUNT(*) - COUNT(DISTINCT student_id) AS failed_count,
       COUNT(*) AS total_count,
       'CRITICAL' AS severity
FROM placewise.silver.students;

-- Check 3: Valid placement_status
SELECT 'placement_status_valid' AS check_name,
       COUNT(*) FILTER (WHERE placement_status NOT IN ('NOT_STARTED','ELIGIBLE','ACTIVE','PLACED','OPTED_OUT')) AS failed_count,
       COUNT(*) AS total_count,
       'ERROR' AS severity
FROM placewise.silver.students;
