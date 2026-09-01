-- =============================================================================
-- PLACEWISE: Authoritative Genie Semantic View — Department Performance
-- Schema: placewise.semantic
-- Grain:  Department x Graduation Year
-- =============================================================================

CREATE OR REPLACE VIEW placewise.semantic.genie_department_performance AS
WITH base AS (
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
        LAG(d.placement_rate) OVER(PARTITION BY d.department_code ORDER BY d.graduation_year) AS prev_placement_rate,
        LAG(d.average_ctc_lpa) OVER(PARTITION BY d.department_code ORDER BY d.graduation_year) AS prev_average_ctc
    FROM placewise.gold.department_placement_performance d
)
SELECT 
    department_code,
    department_name,
    graduation_year,
    total_students,
    eligible_students,
    placed_students,
    placement_rate,
    average_ctc_lpa,
    median_ctc_lpa,
    highest_ctc_lpa,
    prev_placement_rate AS placement_rate_yoy,
    ROUND(placement_rate - COALESCE(prev_placement_rate, placement_rate), 2) AS placement_rate_change_points,
    prev_average_ctc AS average_ctc_yoy,
    DENSE_RANK() OVER(PARTITION BY graduation_year ORDER BY placement_rate DESC) AS rank_within_year
FROM base;
