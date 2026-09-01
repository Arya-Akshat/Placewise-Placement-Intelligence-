import pytest
import pandas as pd
from tests.metrics.placewise.metrics import calculate_skill_gap

def test_skill_gap_basic():
    req = pd.DataFrame({
        'skill_name': ['Python', 'SQL', 'Communication'],
        'required_score': [90, 80, 70],
        'weight': [1.0, 0.8, 0.5],
        'is_mandatory': [True, True, False]
    })
    stu = pd.DataFrame({
        'skill_name': ['Python', 'SQL', 'Communication'],
        'student_score': [70, 60, 85]
    })
    
    # required Python=90, student Python=70, weight=1.0 -> deficit 20
    # required SQL=80, student SQL=60, weight=0.8 -> deficit 16
    # required comm=70, student comm=85, weight=0.5 -> deficit 0
    # weighted_deficit = 20 + 16 = 36
    # total_weight_req = 90*1.0 + 80*0.8 + 70*0.5 = 90 + 64 + 35 = 189
    # pct = 36 / 189 = 0.19047 -> 19.047%
    
    result = calculate_skill_gap(stu, req)
    assert result['skill_gap_percentage'] == pytest.approx(19.0476, rel=0.01)
    assert result['missing_mandatory_skill_count'] == 2

def test_skill_gap_missing_mandatory():
    req = pd.DataFrame({
        'skill_name': ['Java', 'Spring'],
        'required_score': [80, 70],
        'weight': [1.0, 1.0],
        'is_mandatory': [True, True]
    })
    stu = pd.DataFrame({
        'skill_name': ['Java'],
        'student_score': [85]
    })
    
    # Missing Spring entirely
    result = calculate_skill_gap(stu, req)
    assert result['missing_mandatory_skill_count'] == 1
    # total req = 150. deficit = 70. 70/150 = 46.66%
    assert result['skill_gap_percentage'] == pytest.approx(46.66, rel=0.01)
