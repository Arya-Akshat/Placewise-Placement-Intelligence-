checks = [
    # student_placement_profile
    ('gold.student_placement_profile', 'readiness_score_range', 'placement_readiness_score BETWEEN 0 AND 100', 'ERROR'),
    ('gold.student_placement_profile', 'no_null_student', 'student_id IS NOT NULL', 'CRITICAL'),
    
    # skill_match
    ('gold.skill_match', 'match_pct_range', 'match_percentage BETWEEN 0 AND 100', 'ERROR'),
    
    # company_hiring_profile
    ('gold.company_hiring_profile', 'positive_placements', 'total_placements >= 0', 'CRITICAL'),
    
    # rates
    ('gold.company_hiring_profile', 'offer_acc_rate_range', 'offer_acceptance_rate BETWEEN 0 AND 100 OR offer_acceptance_rate IS NULL', 'ERROR'),
    
    # funnel consistency
    ('gold.funnel_metrics', 'funnel_consistency', 'placements_count <= offers_count AND offers_count <= interviews_count', 'CRITICAL')
]
