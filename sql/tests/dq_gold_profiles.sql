-- Check 1: placement_readiness_score bounds
SELECT 'placement_readiness_score_bounds' AS check_name,
       COUNT(*) FILTER (WHERE placement_readiness_score NOT BETWEEN 0 AND 100) AS failed_count,
       COUNT(*) AS total_count,
       'ERROR' AS severity
FROM placewise.gold.student_placement_profile;

-- Check 2: no null student_id
SELECT 'student_id_not_null' AS check_name,
       COUNT(*) FILTER (WHERE student_id IS NULL) AS failed_count,
       COUNT(*) AS total_count,
       'CRITICAL' AS severity
FROM placewise.gold.student_placement_profile;
