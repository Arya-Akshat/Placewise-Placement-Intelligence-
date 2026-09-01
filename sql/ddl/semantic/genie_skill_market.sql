CREATE OR REPLACE VIEW placewise.semantic.genie_skill_market AS
SELECT 
    sk.*,
    students_with_skill_count AS student_supply_ratio,
    job_posting_count AS market_demand_ratio,
    average_skill_gap AS skill_supply_demand_gap,
    CASE WHEN average_skill_gap > 0 AND students_with_skill_count < 50 THEN TRUE ELSE FALSE END AS high_demand_low_supply_flag,
    0.0 AS skill_growth_rate
FROM placewise.gold.skill_demand_profile sk;