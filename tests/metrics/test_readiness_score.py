import pytest
from tests.metrics.placewise.metrics import calculate_readiness

def test_readiness_formula_weights():
    # expected = 80*0.20 + 70*0.25 + 60*0.10 + 50*0.10 + 90*0.20 + 75*0.15 = 73.75
    assert calculate_readiness(80, 70, 60, 50, 90, 75) == pytest.approx(73.75)

def test_readiness_bounded():
    assert calculate_readiness(120, 150, 200, 300, 400, 500) == 100.0
    assert calculate_readiness(-10, -20, -50, 0, 0, 0) == 0.0
