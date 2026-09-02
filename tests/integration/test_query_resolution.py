"""
End-to-end integration test suite for the Placewise query resolution engine.
Tests 30+ diverse real-world queries spanning every supported intent category
to verify correct entity extraction, routing, SQL execution, and response format.
"""
import pytest
from backend.services.mock_engine import process_mock_query


def _query(prompt):
    return process_mock_query(prompt, [])


def _assert_ok(res, expected_source_substr=None, min_rows=0):
    assert res["status"] in ("COMPLETED", "CLARIFICATION_REQUIRED"), f"Unexpected status: {res['status']}"
    assert res.get("content"), "Response has no content"
    assert "couldn't match" not in res["content"].lower(), f"Hit fallback: {res['content'][:120]}"
    assert "couldn't identify" not in res["content"].lower(), f"Hit out-of-domain: {res['content'][:120]}"
    if expected_source_substr:
        att = res.get("attachment", {})
        source = att.get("source_object", "")
        assert expected_source_substr in source, f"Expected source containing '{expected_source_substr}', got '{source}'"
    if min_rows > 0:
        att = res.get("attachment", {})
        table = att.get("table_data", {})
        row_count = len(table.get("rows", []))
        assert row_count >= min_rows, f"Expected >= {min_rows} rows, got {row_count}"


# ========================================================================
# Company Queries
# ========================================================================
class TestCompanyQueries:
    def test_tell_me_about_google(self):
        res = _query("tell me about google")
        _assert_ok(res, "genie_company_intelligence")
        assert "Google" in res["content"]
        assert "80" in res["content"]

    def test_google_placements(self):
        res = _query("google placements")
        _assert_ok(res, "genie_company_intelligence")

    def test_microsoft_informal(self):
        res = _query("what about microsoft?")
        _assert_ok(res, "genie_company_intelligence")
        assert "Microsoft" in res["content"]

    def test_amazon_stats(self):
        res = _query("amazon stats")
        _assert_ok(res, "genie_company_intelligence")
        assert "Amazon" in res["content"]

    def test_flipkart_doing(self):
        res = _query("how is flipkart doing?")
        _assert_ok(res, "genie_company_intelligence")
        assert "Flipkart" in res["content"]

    def test_google_average_package(self):
        res = _query("what is google's average package?")
        _assert_ok(res, "genie_company_intelligence")
        assert "42.57" in res["content"]

    def test_amazon_pay(self):
        res = _query("how much does amazon pay?")
        _assert_ok(res, "genie_company_intelligence")

    def test_google_cse_hires(self):
        res = _query("how many people google hired from computer science")
        _assert_ok(res, "silver.placements")
        assert "29" in res["content"]

    def test_google_total_hires(self):
        res = _query("how many students were placed in Google?")
        _assert_ok(res, "genie_company_intelligence")
        assert "80" in res["content"]


# ========================================================================
# Company Skills / Interview Prep
# ========================================================================
class TestCompanySkillQueries:
    def test_google_interview_prep(self):
        res = _query("how to get placed in google?")
        _assert_ok(res, "job_required_skills")
        assert "Mandatory" in res["content"] or "mandatory" in res["content"].lower()

    def test_google_skills(self):
        res = _query("what skills i need to learn to clear google interview")
        _assert_ok(res, "job_required_skills")


# ========================================================================
# Department Queries
# ========================================================================
class TestDepartmentQueries:
    def test_best_department(self):
        res = _query("best department for placements")
        _assert_ok(res, "genie_department_performance", min_rows=8)

    def test_best_branch_package(self):
        res = _query("which branch gets the best package?")
        _assert_ok(res, "genie_department_performance", min_rows=8)

    def test_worst_department(self):
        res = _query("worst performing department")
        _assert_ok(res, "genie_department_performance", min_rows=8)
        assert "lowest" in res["content"].lower()

    def test_average_all_departments(self):
        res = _query("average package across all departments")
        _assert_ok(res, "genie_department_performance", min_rows=8)
        assert "8.0" in res["content"]

    def test_all_departments_placement_rate(self):
        res = _query("show me all departments placement rate")
        _assert_ok(res, "genie_department_performance", min_rows=8)

    def test_cse_placement_rate(self):
        res = _query("comp sci placement rate")
        _assert_ok(res, "genie_department_performance")
        assert "51.49" in res["content"]

    def test_cse_everything(self):
        res = _query("tell me everything about CSE")
        _assert_ok(res, "genie_department_performance")
        assert "51.49" in res["content"]

    def test_ece_doing(self):
        res = _query("how is ECE doing this year?")
        _assert_ok(res, "genie_department_performance")
        assert "48.86" in res["content"]

    def test_mechanical_avg_package(self):
        res = _query("average package for mechanical students")
        _assert_ok(res, "genie_department_performance")
        assert "Mechanical" in res["content"]

    def test_it_students_placed(self):
        res = _query("how many IT students got placed?")
        _assert_ok(res, "genie_department_performance")
        assert "642" in res["content"]


# ========================================================================
# Comparison & Trend Queries
# ========================================================================
class TestComparisonQueries:
    def test_cse_vs_ece_vs_it(self):
        res = _query("show CSE vs ECE vs IT placement rates")
        _assert_ok(res, "genie_department_performance", min_rows=3)

    def test_improved_departments(self):
        res = _query("Which departments improved placement rate?")
        _assert_ok(res, "genie_department_performance", min_rows=1)
        assert "IT" in res["content"]


# ========================================================================
# Threshold & Filter Queries
# ========================================================================
class TestThresholdQueries:
    def test_total_placed(self):
        res = _query("how many ppl got placed in total")
        _assert_ok(res, "genie_department_performance")
        assert "4,624" in res["content"]

    def test_companies_above_30_lpa(self):
        res = _query("companies paying above 30 lpa")
        _assert_ok(res, "genie_company_intelligence", min_rows=1)

    def test_startups(self):
        res = _query("startups that hired students")
        _assert_ok(res, "genie_company_intelligence", min_rows=1)

    def test_consulting(self):
        res = _query("consulting firms on campus")
        _assert_ok(res, "genie_company_intelligence", min_rows=1)

    def test_best_salary(self):
        res = _query("who offers the best salary?")
        _assert_ok(res, "genie_company_intelligence", min_rows=1)


# ========================================================================
# Recruiter Queries
# ========================================================================
class TestRecruiterQueries:
    def test_top_3_cse_by_package(self):
        res = _query("top 3 companies in CSE by package")
        _assert_ok(res, min_rows=3)

    def test_list_all_companies(self):
        res = _query("list all companies")
        _assert_ok(res, "genie_company_intelligence", min_rows=10)

    def test_target_company(self):
        res = _query("which company should I target?")
        _assert_ok(res, "genie_company_intelligence", min_rows=1)


# ========================================================================
# Edge Cases & Clarifications
# ========================================================================
class TestEdgeCases:
    def test_best_company_clarification(self):
        res = _query("best company")
        assert res["status"] == "CLARIFICATION_REQUIRED"

    def test_placement_solo(self):
        res = _query("placement")
        assert res.get("follow_up_suggestions") and len(res["follow_up_suggestions"]) > 0

    def test_show_all_skills(self):
        res = _query("show all skills")
        _assert_ok(res, "genie_skill_market", min_rows=1)

    def test_highest_package(self):
        res = _query("What was the highest package in 2024?")
        _assert_ok(res, "silver.placements")
        assert "63.96" in res["content"]
