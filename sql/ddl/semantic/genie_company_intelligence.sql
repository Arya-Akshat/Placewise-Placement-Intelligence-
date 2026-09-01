CREATE OR REPLACE VIEW placewise.semantic.genie_company_intelligence AS
SELECT 
    c.*,
    CASE WHEN applications_count > 0 THEN (100 - (shortlisted_count * 100.0 / applications_count)) ELSE 0 END AS hiring_selectivity_score,
    CASE WHEN applications_count > 0 THEN (placements_count * 100.0 / applications_count) ELSE 0 END AS hiring_conversion_score,
    average_ctc_lpa AS company_package_position
FROM placewise.gold.company_hiring_profile c;