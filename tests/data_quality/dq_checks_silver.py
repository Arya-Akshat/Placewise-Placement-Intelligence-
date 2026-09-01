checks = [
    # students
    ('silver.students', 'cgpa_range', 'cgpa BETWEEN 0 AND 10', 'CRITICAL'),
    ('silver.students', 'percentage_range', 'percentage BETWEEN 0 AND 100', 'CRITICAL'),
    ('silver.students', 'backlogs_non_negative', 'backlogs >= 0', 'ERROR'),
    ('silver.students', 'student_id_unique', 'COUNT(DISTINCT student_id) = COUNT(*)', 'CRITICAL'),
    ('silver.students', 'placement_status_valid', "placement_status IN ('NOT_STARTED','ELIGIBLE','ACTIVE','PLACED','OPTED_OUT')", 'ERROR'),
    
    # companies
    ('silver.companies', 'company_id_unique', 'COUNT(DISTINCT company_id) = COUNT(*)', 'CRITICAL'),
    
    # job_postings
    ('silver.job_postings', 'ctc_positive', 'package_min_lpa >= 0', 'ERROR'),
    ('silver.job_postings', 'deadline_after_posting', 'application_deadline > posting_date', 'WARNING'),
    
    # applications
    ('silver.applications', 'student_fk', 'student_id IN (SELECT student_id FROM silver.students)', 'CRITICAL'),
    ('silver.applications', 'posting_fk', 'job_posting_id IN (SELECT job_posting_id FROM silver.job_postings)', 'CRITICAL'),
    
    # interviews
    ('silver.interviews', 'completion_after_schedule', 'completed_at >= scheduled_at', 'ERROR'),
    ('silver.interviews', 'scores_range', 'overall_score BETWEEN 0 AND 100', 'ERROR'),
    
    # offers
    ('silver.offers', 'ctc_positive', 'ctc_lpa > 0', 'CRITICAL'),
    ('silver.offers', 'offer_after_application', 'offer_date >= (SELECT application_date FROM silver.applications WHERE id = application_id)', 'ERROR'),
    
    # student_skills
    ('silver.student_skills', 'proficiency_range', 'proficiency_score BETWEEN 0 AND 100', 'ERROR'),
    
    # placements
    ('silver.placements', 'valid_offer_ref', 'offer_id IN (SELECT offer_id FROM silver.offers)', 'CRITICAL'),
]
