import pytest
from backend.services.entity_extractor import (
    extract_department,
    extract_all_departments,
    extract_company,
    extract_role,
    extract_skills,
    extract_numeric_thresholds,
    parse_query_semantics
)

def test_extract_department_synonyms():
    assert extract_department("what is the placement rate for computer science?") == "CSE"
    assert extract_department("who hired the most in mechanical engineering") == "ME"
    assert extract_department("electronics and communication average package") == "ECE"
    assert extract_department("show artificial intelligence placement stats") == "AIML"
    assert extract_department("civil engineering top recruiters") == "CE"
    assert extract_department("information technology highest CTC") == "IT"
    assert extract_department("electrical and electronics conversion rate") == "EEE"
    assert extract_department("chemical engineering placements") == "CH"

def test_department_pronoun_collision_prevention():
    # Pronoun 'me' should NOT match ME (Mechanical)
    assert extract_department("show me companies offering more than 20 LPA") is None
    assert extract_department("tell me who is the top hirer") is None
    assert extract_department("give it to me") is None

def test_extract_all_departments_for_comparison():
    depts = extract_all_departments("compare CSE and Mechanical placement performance")
    assert "CSE" in depts and "ME" in depts
    assert len(depts) == 2

    depts3 = extract_all_departments("compare Computer Science, Electronics and Civil")
    assert set(depts3) == {"CSE", "ECE", "CE"}

def test_extract_company_aliases_and_exact():
    cid, cname = extract_company("how many students were placed in Google?")
    assert cname == "Google"

    cid, cname = extract_company("what skills are needed for microsoft interview?")
    assert cname == "Microsoft"

    cid, cname = extract_company("tell me about amazon placements")
    assert cname == "Amazon"

    cid, cname = extract_company("what package did nvidia offer?")
    assert cname == "NVIDIA"

def test_extract_role_synonyms():
    assert extract_role("what skills are needed for data analyst?") == "data_analyst"
    assert extract_role("find software engineer requirements") == "software_engineering"
    assert extract_role("data engineering skill profile") == "data_engineering"
    assert extract_role("machine learning openings") == "machine_learning"
    assert extract_role("frontend developer salaries") == "frontend"

def test_extract_numeric_thresholds():
    th1 = extract_numeric_thresholds("show me top 5 companies offering more than 20 LPA")
    assert th1.get("limit") == 5
    assert th1.get("min_ctc_lpa") == 20.0

    th2 = extract_numeric_thresholds("find candidates with CGPA greater than 8.5")
    assert th2.get("min_cgpa") == 8.5

    th3 = extract_numeric_thresholds("show product companies in 2024")
    assert th3.get("company_type") == "PRODUCT"
    assert th3.get("year") == 2024

def test_parse_query_semantics_full():
    sem = parse_query_semantics("how many people google hired from computer science")
    assert sem["company"][1] == "Google"
    assert sem["department"] == "CSE"
