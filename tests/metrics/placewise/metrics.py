import pandas as pd
import numpy as np

def calculate_placement_rate(df: pd.DataFrame) -> float | None:
    if df.empty or 'placement_status' not in df.columns:
        return None
    eligible = df[df['placement_status'].isin(['ELIGIBLE', 'ACTIVE', 'PLACED'])]
    if len(eligible) == 0:
        return None
    placed = eligible[eligible['placement_status'] == 'PLACED']
    return (len(placed) / len(eligible)) * 100.0

def calculate_interview_to_offer_rate(interviews: int, offers: int) -> float | None:
    if interviews <= 0:
        return None
    return (offers / interviews) * 100.0

def calculate_offer_acceptance_rate(offered: int, accepted: int) -> float | None:
    if offered <= 0:
        return None
    return (accepted / offered) * 100.0

def calculate_skill_gap(student_skills_df: pd.DataFrame, required_skills_df: pd.DataFrame) -> dict:
    if required_skills_df.empty:
        return {'skill_gap_percentage': 0.0, 'missing_mandatory_skill_count': 0}
    
    # Simple join mock
    df = required_skills_df.merge(student_skills_df, on='skill_name', how='left')
    df['student_score'] = df['student_score'].fillna(0)
    
    missing_mandatory = df[(df['is_mandatory'] == True) & (df['student_score'] < df['required_score'])]
    missing_count = len(missing_mandatory)
    
    total_weight = 0
    weighted_deficit = 0
    for _, row in df.iterrows():
        weight = row.get('weight', 1.0)
        req = row['required_score']
        stu = row['student_score']
        total_weight += (req * weight)
        if stu < req:
            weighted_deficit += ((req - stu) * weight)
            
    if total_weight == 0:
        return {'skill_gap_percentage': 0.0, 'missing_mandatory_skill_count': missing_count}
        
    gap_pct = (weighted_deficit / total_weight) * 100.0
    return {
        'skill_gap_percentage': min(100.0, max(0.0, gap_pct)),
        'missing_mandatory_skill_count': missing_count
    }

def calculate_readiness(academic: float, skill: float, internship: float, project: float, interview: float, conversion: float) -> float:
    # Weights
    w = {
        'academic': 0.20,
        'skill': 0.25,
        'internship': 0.10,
        'project': 0.10,
        'interview': 0.20,
        'conversion': 0.15
    }
    score = (
        academic * w['academic'] +
        skill * w['skill'] +
        internship * w['internship'] +
        project * w['project'] +
        interview * w['interview'] +
        conversion * w['conversion']
    )
    return max(0.0, min(100.0, score))

def calculate_application_to_shortlist_rate(applications: int, shortlisted: int) -> float | None:
    if applications <= 0:
        return None
    return (shortlisted / applications) * 100.0
