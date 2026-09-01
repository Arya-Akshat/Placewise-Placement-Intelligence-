import pytest
import pandas as pd
import numpy as np

# Root level conftest for any global fixtures
@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({'id': [1, 2, 3], 'value': [10, 20, 30]})
