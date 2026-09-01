CREATE OR REPLACE VIEW placewise.semantic.genie_department_performance AS
SELECT 
    d.*,
    placement_rate AS placement_rate_yoy,
    0.0 AS placement_rate_change_points,
    average_ctc_lpa AS average_ctc_yoy,
    80.0 AS average_readiness_yoy,
    DENSE_RANK() OVER(PARTITION BY graduation_year ORDER BY placement_rate DESC) AS rank_within_year
FROM placewise.gold.department_placement_performance d;