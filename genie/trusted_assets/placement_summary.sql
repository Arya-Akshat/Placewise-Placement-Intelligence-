-- =============================================================================
-- TRUSTED ASSET: Placewise Department Placement & CTC Summary
-- Verified Deterministic Metric Aggregation
-- =============================================================================
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
    d.placement_rate_change_points,
    d.rank_within_year
FROM placewise.semantic.genie_department_performance d
WHERE d.graduation_year = :graduation_year
ORDER BY d.placement_rate DESC;
