from tests.metrics.placewise.metrics import calculate_interview_to_offer_rate, calculate_offer_acceptance_rate

def test_interview_to_offer_rate():
    assert calculate_interview_to_offer_rate(interviews=100, offers=20) == 20.0

def test_interview_to_offer_rate_zero():
    assert calculate_interview_to_offer_rate(interviews=0, offers=0) is None

def test_offer_acceptance_rate():
    assert calculate_offer_acceptance_rate(offered=10, accepted=8) == 80.0

def test_offer_acceptance_rate_zero():
    assert calculate_offer_acceptance_rate(offered=0, accepted=0) is None
