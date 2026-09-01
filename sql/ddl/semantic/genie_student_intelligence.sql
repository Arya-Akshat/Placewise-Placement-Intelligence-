CREATE OR REPLACE VIEW placewise.semantic.genie_student_intelligence AS
SELECT 
    s.*,
    CASE 
        WHEN placement_readiness_score >= 80 THEN 'A'
        WHEN placement_readiness_score >= 60 THEN 'B'
        WHEN placement_readiness_score >= 40 THEN 'C'
        ELSE 'D'
    END AS readiness_band,
    CASE 
        WHEN accepted_offers_count > 0 THEN 'PLACED'
        WHEN offers_count > 0 THEN 'OFFERED'
        WHEN interviews_count > 0 THEN 'INTERVIEWING'
        WHEN applications_count > 0 THEN 'APPLYING'
        ELSE 'INACTIVE'
    END AS placement_outcome_stage,
    (internship_score + project_score) / 2 AS experience_strength_score,
    CASE
        WHEN applications_count > 20 THEN 'HIGH'
        WHEN applications_count > 5 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS application_activity_level,
    CASE
        WHEN highest_offer_lpa >= 15 THEN 'TIER 1'
        WHEN highest_offer_lpa >= 8 THEN 'TIER 2'
        WHEN highest_offer_lpa >= 4 THEN 'TIER 3'
        ELSE 'UNPLACED'
    END AS offer_quality_band,
    application_conversion_score AS career_alignment_score,
    verified_skill_count AS top_skill_count,
    0 AS missing_core_skill_count,
    placement_readiness_score AS placement_readiness_confidence
FROM placewise.gold.student_placement_profile s;