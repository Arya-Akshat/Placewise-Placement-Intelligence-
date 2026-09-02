import pytest
from backend.services.guardrails import check_guardrails

def test_guardrails_profanity_blocked():
    r1 = check_guardrails("how to fuck a girl")
    assert not r1.is_allowed
    assert r1.category == "INAPPROPRIATE"
    assert "respectful and placement-related" in r1.response_text

    r2 = check_guardrails("you asshole")
    assert not r2.is_allowed
    assert r2.category == "INAPPROPRIATE"

def test_guardrails_greetings():
    r = check_guardrails("Hello")
    assert not r.is_allowed
    assert r.category == "GREETING"
    assert "Placewise" in r.response_text

    r2 = check_guardrails("hi")
    assert not r2.is_allowed
    assert r2.category == "GREETING"

def test_guardrails_out_of_domain():
    r = check_guardrails("How do I cook pasta?")
    assert not r.is_allowed
    assert r.category == "OUT_OF_DOMAIN"
    assert "campus placement analytics" in r.response_text

def test_guardrails_placement_allowed():
    r1 = check_guardrails("What is the placement rate for CSE in 2024?")
    assert r1.is_allowed
    assert r1.category == "SAFE"

    r2 = check_guardrails("Which companies hired the most students?")
    assert r2.is_allowed
    assert r2.category == "SAFE"

    r3 = check_guardrails("Find the best candidates for Data Engineering")
    assert r3.is_allowed
    assert r3.category == "SAFE"
