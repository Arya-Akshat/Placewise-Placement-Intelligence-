-- =============================================================================
-- PLACEWISE: Authoritative Genie Semantic View — Student Job Match
-- Schema: placewise.semantic
-- Grain:  Student x Job Posting
-- =============================================================================

CREATE OR REPLACE VIEW placewise.semantic.genie_student_job_match AS
SELECT 
    m.student_id,
    m.job_posting_id,
    m.weighted_deficit,
    m.skill_match_percentage,
    ROUND(100.0 - m.skill_match_percentage, 2) AS skill_gap_percentage,
    m.missing_mandatory_skill_count,
    ROUND(LEAST(100.0, GREATEST(0.0, m.skill_match_percentage * 0.40 + 60.0 * 0.60)), 2) AS ranking_score,
    CASE 
        WHEN m.skill_match_percentage >= 85.0 THEN 'EXCELLENT'
        WHEN m.skill_match_percentage >= 70.0 THEN 'STRONG'
        WHEN m.skill_match_percentage >= 50.0 THEN 'GOOD'
        WHEN m.skill_match_percentage >= 35.0 THEN 'FAIR'
        ELSE 'POOR'
    END AS candidate_fit_band
FROM placewise.gold.student_job_skill_match m;
