import pytest
import pandas as pd

@pytest.fixture
def empty_students():
    return pd.DataFrame(columns=['student_id', 'placement_status'])

@pytest.fixture
def basic_students():
    return pd.DataFrame({
        'student_id': range(1, 11),
        'placement_status': ['PLACED']*8 + ['ELIGIBLE']*2
    })
