import pandas as pd
from tests.metrics.placewise.metrics import calculate_placement_rate

def test_placement_rate_basic(basic_students):
    # 10 eligible, 8 placed -> 80%
    assert calculate_placement_rate(basic_students) == 80.0

def test_placement_rate_zero_eligible():
    df = pd.DataFrame({'student_id': [1, 2], 'placement_status': ['NOT_STARTED', 'OPTED_OUT']})
    assert calculate_placement_rate(df) is None

def test_placement_rate_all_placed():
    df = pd.DataFrame({'student_id': range(5), 'placement_status': ['PLACED']*5})
    assert calculate_placement_rate(df) == 100.0

def test_placement_rate_empty(empty_students):
    assert calculate_placement_rate(empty_students) is None
