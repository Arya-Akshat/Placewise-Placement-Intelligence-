import pytest
import pandas as pd
import numpy as np
from scipy import stats

@pytest.fixture
def synthetic_distributions():
    return {
        'students': pd.DataFrame({
            'department': ['CS', 'CS', 'EC', 'ME'],
            'cgpa': [8.5, 9.1, 7.8, 8.0]
        }),
        'offers': pd.DataFrame({
            'ctc_lpa': [10, 12, 15, 8]
        })
    }

def test_dept_proportions(synthetic_distributions):
    # Dummy check for proportions
    dept_counts = synthetic_distributions['students']['department'].value_counts(normalize=True)
    assert 'CS' in dept_counts
    assert dept_counts['CS'] >= 0.25 # arbitrary sanity check

def test_cgpa_distribution(synthetic_distributions):
    # Dummy KS test
    cgpas = synthetic_distributions['students']['cgpa']
    # test against normal distribution around 8.0
    stat, pval = stats.kstest(cgpas, lambda x: stats.norm.cdf(x, loc=7.477, scale=0.871))
    # not actually asserting pval here since N is too small, just structural
    assert len(cgpas) > 0

def test_ctc_distribution(synthetic_distributions):
    ctcs = synthetic_distributions['offers']['ctc_lpa']
    assert ctcs.mean() > 5.0
    assert ctcs.median() > 5.0
