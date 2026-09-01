CREATE OR REPLACE VIEW placewise.semantic.genie_student_job_match AS
SELECT 
    m.*,
    skill_match_percentage AS ranking_score,
    CASE 
        WHEN skill_match_percentage >= 80 THEN 'HIGH FIT'
        WHEN skill_match_percentage >= 50 THEN 'MEDIUM FIT'
        ELSE 'LOW FIT'
    END AS candidate_fit_band
FROM placewise.gold.student_job_skill_match m;