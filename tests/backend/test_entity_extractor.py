import pytest
from backend.services.entity_extractor import (
    extract_department,
    extract_all_departments,
    extract_company,
    extract_role,
    extract_skills,
    extract_numeric_thresholds,
    classify_intents,
    parse_query_semantics
)


class TestDepartmentExtraction:
    def test_full_name_synonyms(self):
        assert extract_department("what is the placement rate for computer science?") == "CSE"
        assert extract_department("who hired the most in mechanical engineering") == "ME"
        assert extract_department("electronics and communication average package") == "ECE"
        assert extract_department("show artificial intelligence placement stats") == "AIML"
        assert extract_department("civil engineering top recruiters") == "CE"
        assert extract_department("information technology highest CTC") == "IT"
        assert extract_department("electrical and electronics conversion rate") == "EEE"
        assert extract_department("chemical engineering placements") == "CH"

    def test_short_codes(self):
        assert extract_department("CSE placement rate") == "CSE"
        assert extract_department("show ECE stats") == "ECE"
        assert extract_department("AIML department performance") == "AIML"
        assert extract_department("EEE placements in 2024") == "EEE"

    def test_informal_synonyms(self):
        assert extract_department("comp sci placement rate") == "CSE"
        assert extract_department("mech department hires") == "ME"

    def test_pronoun_collision_prevention(self):
        """Pronouns 'me' and 'it' should NOT match ME/IT without context."""
        assert extract_department("show me companies offering more than 20 LPA") is None
        assert extract_department("tell me who is the top hirer") is None
        assert extract_department("give it to me") is None

    def test_it_department_with_context(self):
        """'IT' should match when placement context words are present."""
        assert extract_department("how many IT students got placed?") == "IT"
        assert extract_department("IT placement rate in 2024") == "IT"
        assert extract_department("IT department performance") == "IT"

    def test_longest_match_wins(self):
        """Electrical and electronics should match EEE, not ECE."""
        assert extract_department("electrical and electronics conversion rate") == "EEE"
        assert extract_department("electronics and communication placement rate") == "ECE"


class TestMultiDepartmentExtraction:
    def test_two_departments(self):
        depts = extract_all_departments("compare CSE and Mechanical placement performance")
        assert "CSE" in depts and "ME" in depts
        assert len(depts) == 2

    def test_three_departments(self):
        depts = extract_all_departments("show CSE vs ECE vs IT placement rates")
        assert set(depts) >= {"CSE", "ECE"}
        # IT should also be detected with context
        assert "IT" in depts

    def test_no_duplicates(self):
        depts = extract_all_departments("compare Computer Science and CSE")
        assert depts.count("CSE") == 1


class TestCompanyExtraction:
    def test_known_aliases(self):
        cid, cname = extract_company("how many students were placed in Google?")
        assert cname == "Google"

        cid, cname = extract_company("what skills are needed for microsoft interview?")
        assert cname == "Microsoft"

        cid, cname = extract_company("tell me about amazon placements")
        assert cname == "Amazon"

        cid, cname = extract_company("what package did nvidia offer?")
        assert cname == "NVIDIA"

    def test_informal_phrasing(self):
        cid, cname = extract_company("tell me about google")
        assert cname == "Google"

        cid, cname = extract_company("google placements")
        assert cname == "Google"

        cid, cname = extract_company("amazon stats")
        assert cname == "Amazon"

        cid, cname = extract_company("how is flipkart doing?")
        assert cname == "Flipkart"

    def test_no_false_positive(self):
        assert extract_company("what is the placement rate for CSE?") is None
        assert extract_company("which department has the highest package?") is None


class TestRoleExtraction:
    def test_role_synonyms(self):
        assert extract_role("what skills are needed for data analyst?") == "data_analyst"
        assert extract_role("find software engineer requirements") == "software_engineering"
        assert extract_role("data engineering skill profile") == "data_engineering"
        assert extract_role("machine learning openings") == "machine_learning"
        assert extract_role("frontend developer salaries") == "frontend"
        assert extract_role("backend developer requirements") == "backend"

    def test_longest_match_wins(self):
        """'frontend developer' should match frontend, not software_engineering via 'developer'."""
        assert extract_role("frontend developer salaries") == "frontend"
        assert extract_role("backend developer requirements") == "backend"


class TestNumericThresholds:
    def test_top_n_and_ctc(self):
        th = extract_numeric_thresholds("show me top 5 companies offering more than 20 LPA")
        assert th.get("limit") == 5
        assert th.get("min_ctc_lpa") == 20.0

    def test_cgpa(self):
        th = extract_numeric_thresholds("find candidates with CGPA greater than 8.5")
        assert th.get("min_cgpa") == 8.5

    def test_company_type_and_year(self):
        th = extract_numeric_thresholds("show product companies in 2024")
        assert th.get("company_type") == "PRODUCT"
        assert th.get("year") == 2024

    def test_informal_pay_threshold(self):
        th = extract_numeric_thresholds("companies paying above 30 lpa")
        assert th.get("min_ctc_lpa") == 30.0


class TestIntentClassification:
    def test_company_info(self):
        intents = classify_intents("tell me about google")
        assert "company_info" in intents

    def test_placement_count(self):
        intents = classify_intents("how many students got placed?")
        assert "placement_count" in intents

    def test_package_inquiry(self):
        intents = classify_intents("what is the average salary?")
        assert "package_inquiry" in intents

    def test_skill_inquiry(self):
        intents = classify_intents("what skills are needed for google interview?")
        assert "skill_inquiry" in intents

    def test_comparison(self):
        intents = classify_intents("compare CSE and ECE")
        assert "comparison" in intents

    def test_ranking(self):
        intents = classify_intents("which is the best department?")
        assert "ranking" in intents

    def test_trend(self):
        intents = classify_intents("which departments improved placement rate?")
        assert "trend" in intents


class TestFullParsing:
    def test_company_and_department(self):
        sem = parse_query_semantics("how many people google hired from computer science")
        assert sem["company"][1] == "Google"
        assert sem["department"] == "CSE"

    def test_department_only(self):
        sem = parse_query_semantics("CSE placement rate 2024")
        assert sem["department"] == "CSE"
        assert sem["company"] is None

    def test_threshold_only(self):
        sem = parse_query_semantics("show product companies offering more than 20 LPA")
        assert sem["thresholds"]["company_type"] == "PRODUCT"
        assert sem["thresholds"]["min_ctc_lpa"] == 20.0
        assert sem["company"] is None
