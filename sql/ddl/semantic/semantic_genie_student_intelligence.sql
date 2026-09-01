-- =============================================================================
-- PLACEWISE: Authoritative Genie Semantic View — Student Intelligence
-- Schema: placewise.semantic
-- Grain:  One row per student
-- =============================================================================

CREATE OR REPLACE VIEW placewise.semantic.genie_student_intelligence AS
SELECT 
    s.student_id,
    s.full_name,
    s.gender,
    s.university_roll_no,
    s.cohort_id,
    s.department_id,
    s.department_name,
    s.department_code,
    s.program_id,
    s.program_name,
    s.degree_type,
    s.batch_label,
    s.admission_year,
    s.graduation_year,
    s.current_semester,
    s.placement_status,
    s.preferred_role,
    s.preferred_location,
    s.work_authorization,
    s.cgpa,
    s.percentage,
    s.backlogs,
    s.attendance_percentage,

    -- Governed Component Scores (0-100)
    s.academic_score,
    s.skill_score,
    s.internship_score,
    s.project_score,
    s.interview_score,
    s.application_conversion_score,

    -- Placement Readiness Score (Weighted 0-100 index)
    s.placement_readiness_score,

    -- Governed Categorical Readiness Band
    CASE 
        WHEN s.placement_readiness_score >= 90.0 THEN 'VERY_HIGH'
        WHEN s.placement_readiness_score >= 75.0 THEN 'HIGH'
        WHEN s.placement_readiness_score >= 60.0 THEN 'MODERATE'
        WHEN s.placement_readiness_score >= 40.0 THEN 'LOW'
        ELSE 'VERY_LOW'
    END AS readiness_band,

    -- Governed Placement Stage
    CASE 
        WHEN s.placed_flag = 1 THEN 'PLACED'
        WHEN s.accepted_offers_count > 0 THEN 'OFFER_ACCEPTED'
        WHEN s.offers_count > 0 THEN 'OFFERED'
        WHEN s.placement_status = 'ACTIVE' THEN 'ACTIVE'
        WHEN s.placement_status = 'OPTED_OUT' THEN 'OPTED_OUT'
        WHEN s.placement_status = 'ELIGIBLE' THEN 'ELIGIBLE'
        ELSE 'NOT_STARTED'
    END AS placement_outcome_stage,

    -- Experience & Alignment Scores
    ROUND(LEAST(100.0, GREATEST(0.0, s.internship_score * 0.70 + s.project_score * 0.30)), 2) AS experience_strength_score,
    ROUND(LEAST(100.0, GREATEST(0.0, s.skill_score * 0.50 + s.project_score * 0.30 + s.internship_score * 0.20)), 2) AS career_alignment_score,

    -- Activity & Offer Quality
    CASE
        WHEN s.applications_count >= 15 THEN 'VERY_HIGH'
        WHEN s.applications_count >= 8  THEN 'HIGH'
        WHEN s.applications_count >= 4  THEN 'MODERATE'
        WHEN s.applications_count >= 1  THEN 'LOW'
        ELSE 'NONE'
    END AS application_activity_level,

    CASE
        WHEN s.highest_offer_lpa >= 20.0 THEN 'PREMIUM'
        WHEN s.highest_offer_lpa >= 12.0 THEN 'HIGH'
        WHEN s.highest_offer_lpa >= 6.0  THEN 'MID'
        WHEN s.highest_offer_lpa > 0.0   THEN 'ENTRY'
        ELSE 'NO_OFFER'
    END AS offer_quality_band,

    -- Readiness Confidence (Data Completeness)
    CASE 
        WHEN s.total_interview_rounds >= 2 AND s.verified_skill_count >= 5 THEN 'HIGH'
        WHEN s.total_interview_rounds >= 1 OR s.verified_skill_count >= 3 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS placement_readiness_confidence,

    -- Skill & Experience Details
    s.verified_skill_count,
    s.technical_skill_score,
    s.soft_skill_score,
    s.internship_count,
    s.internship_months,
    s.ppo_count,
    s.project_count,
    s.certification_count,
    s.course_count,

    -- Funnel Counts & Conversion Rates
    s.applications_count,
    s.shortlisted_count,
    s.interviews_count,
    s.offers_count,
    s.accepted_offers_count,
    s.total_interview_rounds,
    s.interview_clears,
    s.average_interview_score,
    s.best_interview_score,
    s.application_to_shortlist_rate,
    s.shortlist_to_interview_rate,
    s.interview_to_offer_rate,
    s.application_to_offer_rate,
    s.offer_acceptance_rate,

    -- Financials & Outcomes
    s.highest_offer_lpa,
    s.average_offer_lpa,
    s.accepted_offer_lpa,
    s.placed_flag,
    s.placed_ctc_lpa,

    -- Diagnostic Indicators
    s.strong_academic_weak_interview_flag,
    s.unplaced_eligible_flag,
    s.profile_computed_at

FROM placewise.gold.student_placement_profile s;
