import pytest
import pandas as pd

# Dummy synthetic_data fixture, in reality this would load generated files
@pytest.fixture
def synthetic_data():
    return {
        'students': pd.DataFrame({'student_id': [1, 2], 'cgpa': [8.5, 9.0]}),
        'applications': pd.DataFrame({'application_id': [10, 11], 'student_id': [1, 2]}),
        'interviews': pd.DataFrame({'interview_id': [100], 'application_id': [10]}),
        'offers': pd.DataFrame({'offer_id': [1000], 'application_id': [10], 'ctc_lpa': [12.5]}),
        'placements': pd.DataFrame({'placement_id': [10000], 'offer_id': [1000]}),
        'student_skills': pd.DataFrame({'student_id': [1], 'proficiency_score': [85]})
    }

def test_no_orphan_applications(synthetic_data):
    apps = synthetic_data['applications']
    students = synthetic_data['students']
    assert apps['student_id'].isin(students['student_id']).all()

def test_no_orphan_interviews(synthetic_data):
    ints = synthetic_data['interviews']
    apps = synthetic_data['applications']
    assert ints['application_id'].isin(apps['application_id']).all()

def test_placement_funnel_consistency(synthetic_data):
    # placements <= offers <= applications
    apps_cnt = len(synthetic_data['applications'])
    offers_cnt = len(synthetic_data['offers'])
    places_cnt = len(synthetic_data['placements'])
    assert places_cnt <= offers_cnt <= apps_cnt

def test_cgpa_distribution(synthetic_data):
    mean_cgpa = synthetic_data['students']['cgpa'].mean()
    assert 6.0 <= mean_cgpa <= 9.5

def test_skill_proficiency_range(synthetic_data):
    scores = synthetic_data['student_skills']['proficiency_score']
    assert scores.between(0, 100).all()

def test_ctc_positive(synthetic_data):
    ctcs = synthetic_data['offers']['ctc_lpa']
    assert (ctcs > 0).all()
