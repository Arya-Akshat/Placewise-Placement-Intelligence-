# Placewise Databricks Metric Verification & Grain Quality Report

**Verification Engine:** DuckDB Mirror / Databricks SQL  
**Validation Date:** 2026-09-01  
**Integrity Status:** CERTIFIED (100% Pass)  

---

## 1. Primary Key & Grain Integrity Results

| Semantic Object | Declared Grain | Total Rows | Distinct Primary Keys | Invariant Check | Status |
|---|---|---|---|---|---|
| `semantic.genie_student_intelligence` | One row per student (student_id) | 50,000 | 50,000 | `COUNT(*) == COUNT(DISTINCT PK)` | **PASS** |
| `semantic.genie_company_intelligence` | One row per company (company_id) | 600 | 600 | `COUNT(*) == COUNT(DISTINCT PK)` | **PASS** |
| `semantic.genie_department_performance` | Department x Graduation Year | 32 | 32 | `COUNT(*) == COUNT(DISTINCT PK)` | **PASS** |
| `semantic.genie_skill_market` | One row per skill (skill_id) | 66 | 66 | `COUNT(*) == COUNT(DISTINCT PK)` | **PASS** |
| `semantic.genie_student_job_match` | Student x Job Posting | 125,002,500 | 125,002,500 | `COUNT(*) == COUNT(DISTINCT PK)` | **PASS** |

---

## 2. Business Metric Reconciliation Matrix (Raw Silver vs. Semantic Layer)

All critical placement, financial, funnel, and readiness metrics were independently recomputed from raw Silver tables and compared against the curated `placewise.semantic.*` views:

| Metric Name | Raw Calculation (Silver) | Semantic Layer Output | Absolute Variance | Tolerance | Verification Result |
|---|---|---|---|---|---|
| **Placement Rate (CSE 2024)** | 51.49% | 51.49% | 0.0000 % | $\le 0.01$ % | **PASS (100% MATCH)** |
| **Placement Rate (ECE 2024)** | 48.86% | 48.86% | 0.0000 % | $\le 0.01$ % | **PASS (100% MATCH)** |
| **Average Placed CTC (Overall)** | ₹8.29 LPA | ₹8.29 LPA | 0.0000 LPA | $\le 0.01$ LPA | **PASS (100% MATCH)** |
| **Median Placed CTC (Overall)** | ₹6.06 LPA | ₹6.06 LPA | 0.0000 LPA | $\le 0.01$ LPA | **PASS (100% MATCH)** |
| **Highest Placed CTC (Overall)** | ₹63.96 LPA | ₹63.96 LPA | 0.0000 LPA | $\le 0.01$ LPA | **PASS (100% MATCH)** |
| **Offer Acceptance Rate** | 82.11% | 82.11% | 0.0000 % | $\le 0.01$ % | **PASS (100% MATCH)** |
| **Interview to Offer Rate** | 54.18% | 54.18% | 0.0000 % | $\le 0.01$ % | **PASS (100% MATCH)** |

---

## 3. Placement Readiness Component Verification

The canonical student placement readiness score formula was audited across all 50,000 students:

$$\text{Readiness} = \text{Academic}\,(20\%) + \text{Skill}\,(25\%) + \text{Internship}\,(10\%) + \text{Project}\,(10\%) + \text{Interview}\,(20\%) + \text{Conversion}\,(15\%)$$

- **Boundedness Test**: $0.00 \le \text{Score} \le 100.00$ verified across 100% of student rows.
- **Null Handling Test**: 0 NULL scores generated.
- **Component Auditability**: All 6 underlying component scores remain preserved and independently queryable.
