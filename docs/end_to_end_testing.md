# Placewise End-to-End Testing & Scenario Verification Report

**Date:** 2026-09-01  
**Execution Engine:** `scripts/test_app_scenarios.py`  
**Result:** 12 / 12 Scenarios Passed (**100% Pass Rate**)  

---

## Scenario Verification Matrix

| Scenario ID | Test Prompt | Primary Intent | Expected UI Attachment | Status |
|---|---|---|---|---|
| **SCENARIO 1** | *"What is the placement rate for CSE in 2024?"* | Department Placement Rate | KPI Cards (`51.49%`, $1,159$ placed) + Table | **PASS** |
| **SCENARIO 2** | *"How does that compare with ECE?"* | Follow-Up Branch Comparison | Bar Chart (`CSE 51.49%` vs `ECE 48.86%`) | **PASS** |
| **SCENARIO 3** | *"What are the top 10 demanded skills?"* | Market Skill Demand | Table & Bar Chart (`demand_rank`) | **PASS** |
| **SCENARIO 4** | *"Show high-readiness students without offers."* | Student Discovery | Table (`placement_readiness_score DESC`) | **PASS** |
| **SCENARIO 5** | *"Which companies hired the most students?"* | Recruiter Analytics | Bar Chart (`placements_count DESC`) | **PASS** |
| **SCENARIO 6** | *"Which departments improved placement rate?"* | YoY Improvement Trend | Bar Chart (`placement_rate_change_points > 0`) | **PASS** |
| **SCENARIO 7** | *"Which skills have high demand but low supply?"* | Skill Supply-Demand Gap | Table (`high_demand_low_supply_flag = TRUE`) | **PASS** |
| **SCENARIO 8** | *"Find the strongest Data Engineering candidates."* | Candidate Recommendation | Candidate Matching Table (Readiness & Skills) | **PASS** |
| **SCENARIO 9** | *"What is the placement rate?"* | Ambiguity Trigger | `<ClarificationPrompt />` with batch/branch chips | **PASS** |
| **SCENARIO 10**| *"Which company performed best?"* | Metric Ambiguity | `<ClarificationPrompt />` with volume/CTC/conversion chips | **PASS** |
| **SCENARIO 11**| *"Why did Mechanical placement performance change?"* | Agent Mode Multi-Step | `<AgentAnalysis />` with 4 Evidence Cards & Findings | **PASS** |
| **SCENARIO 12**| *"Show me all student-job matches."* | Large Result Truncation | Truncated Notice (First 10 of $125\text{M}$ rows) | **PASS** |
