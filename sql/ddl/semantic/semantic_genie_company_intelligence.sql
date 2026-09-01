-- =============================================================================
-- PLACEWISE: Authoritative Genie Semantic View — Company Intelligence
-- Schema: placewise.semantic
-- Grain:  One row per company
-- =============================================================================

CREATE OR REPLACE VIEW placewise.semantic.genie_company_intelligence AS
SELECT 
    c.company_id,
    c.company_name,
    c.industry,
    c.company_type,
    c.product_or_service,
    c.job_postings_count,
    c.openings_count,
    c.applications_count,
    c.shortlisted_count,
    c.interviews_count,
    c.offers_count,
    c.accepted_offers_count,
    c.placements_count,
    c.average_ctc_lpa,
    c.median_ctc_lpa,
    c.highest_ctc_lpa,
    c.lowest_ctc_lpa,
    c.application_to_interview_rate,
    c.interview_to_offer_rate,
    c.offer_acceptance_rate,
    c.application_to_placement_rate,
    c.average_interview_score,

    -- Selectivity & Conversion Index
    CASE WHEN c.applications_count > 0 
         THEN ROUND(100.0 - (c.offers_count * 100.0 / c.applications_count), 2)
         ELSE 50.0 
    END AS hiring_selectivity_score,

    CASE WHEN c.applications_count > 0 
         THEN ROUND((c.placements_count * 100.0 / c.applications_count), 2)
         ELSE 0.0 
    END AS hiring_conversion_score,

    -- Package Position
    CASE 
        WHEN c.average_ctc_lpa >= 15.0 THEN 'TOP_DECILE'
        WHEN c.average_ctc_lpa >= 8.0  THEN 'ABOVE_MEDIAN'
        WHEN c.average_ctc_lpa >= 5.0  THEN 'AROUND_MEDIAN'
        WHEN c.average_ctc_lpa > 0.0   THEN 'BELOW_MEDIAN'
        ELSE 'NOT_AVAILABLE'
    END AS company_package_position

FROM placewise.gold.company_hiring_profile c;
