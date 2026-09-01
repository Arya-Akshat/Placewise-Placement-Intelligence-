# Placewise Placement Intelligence — Databricks Genie Agent Guide

**Agent Name:** `Placewise Placement Intelligence`  
**Target Catalog:** `PLACEWISE`  
**Primary Semantics:** `PLACEWISE.SEMANTIC`  
**Target Audience:** Placement Cell Officers, Department Heads/Faculty, Corporate Recruiters, Student Advisors  

---

## 1. Architecture & Core Philosophy

Placewise is centered around a governed semantic layer on Databricks Unity Catalog. Genie does not construct business logic from raw tables; rather, it queries 5 authoritative curated semantic objects with strict metric definitions.

```
                  ┌─────────────────────────────────────────┐
                  │          Databricks Genie Agent         │
                  │   (Placewise Placement Intelligence)    │
                  └────────────────────┬────────────────────┘
                                       │
                         Translates Natural Language
                         into Governed SQL Queries
                                       │
                  ┌────────────────────▼────────────────────┐
                  │       PLACWISE.SEMANTIC Layer           │
                  ├─────────────────────────────────────────┤
                  │ 1. genie_student_intelligence           │
                  │ 2. genie_company_intelligence           │
                  │ 3. genie_department_performance         │
                  │ 4. genie_skill_market                   │
                  │ 5. genie_student_job_match              │
                  └────────────────────┬────────────────────┘
                                       │
                  ┌────────────────────▼────────────────────┐
                  │         PLACEWISE.GOLD (Delta)          │
                  │       Pre-aggregated Fact & Dims        │
                  └─────────────────────────────────────────┘
```

---

## 2. The 5 Curated Semantic Objects

| Object Name | Grain | Description & Primary Use Cases |
|---|---|---|
| `semantic.genie_student_intelligence` | One row per student ($50,000$ rows) | Individual student profiles, academic scores, skill proficiencies, readiness bands, application funnels, placement outcomes, and compensation. |
| `semantic.genie_company_intelligence` | One row per employer ($600$ rows) | Company hiring analytics, drive statistics, CTC packages, interview-to-offer conversions, and selectivity scores. |
| `semantic.genie_department_performance` | Department $	imes$ Graduation Year ($32$ rows) | Cohort benchmarks, historical placement rates, YoY percentage point changes, and salary trends. |
| `semantic.genie_skill_market` | One row per skill ($66$ rows) | Market demand vs student supply, skill gaps, openings count, and high-demand low-supply flags. |
| `semantic.genie_student_job_match` | Student $	imes$ Job Posting | Candidate recommendation engine, skill match %, missing mandatory skills, and fit bands. |

---

## 3. Global Instructions for Genie

1. **Governed Grounding**: Answer strictly using the 5 `semantic.genie_*` objects. Never invent formulas or extrapolate unverified metrics.
2. **Placement Definition**: A student is placed ONLY if `placed_flag = 1`. Extended offers or pending interviews do not count toward placed totals.
3. **Compensation Reporting**: Always report compensation in LPA using `average_ctc_lpa` or `placed_ctc_lpa`.
4. **Time & Batch Semantics**:
   * "This year" defaults to the latest completed graduation year (`2024` or active cycle `2025`).
   * When comparing trends, compare equivalent graduation cohorts.
5. **Clarification Behavior**:
   * If a user asks "Which company performed best?", clarify whether they mean *number of hires*, *highest package*, or *interview conversion rate*.
   * If a user asks "Show top candidates", clarify the target role, skill, or department.

---

## 4. Agent Mode for Complex Multi-Step Reasoning

For multi-faceted analytical questions, Genie activates Agent Mode with structured step-by-step reasoning:

* **Scenario: Explaining Department Placement Decline**:
  1. Query `semantic.genie_department_performance` for YoY placement rate and CTC change.
  2. Query `semantic.genie_student_intelligence` to inspect funnel drop-offs (Shortlist $	o$ Interview $	o$ Offer).
  3. Query `semantic.genie_skill_market` for market demand shifts impacting that department's core skills.
  4. Synthesize observations using factual data ("associated with lower interview conversion in Core roles").

---

## 5. Databricks Workspace Deployment Steps

1. **Catalog Setup**: Run `databricks/catalogs/catalog_setup.sql` to initialize `placewise`.
2. **Schema & DDL**: Execute SQL scripts in `databricks/schemas/` and `sql/ddl/`.
3. **Data Loading**: Ingest Bronze/Silver data and execute Gold transformations via `scripts/load_database.py`.
4. **Genie Space Creation**:
   * Navigate to **Genie** in Databricks Workspace.
   * Create Space: `Placewise Placement Intelligence`.
   * Connect to SQL Warehouse and select the 5 `placewise.semantic.genie_*` views.
   * Paste Global Instructions from `genie/instructions/global_instructions.md`.
   * Add Curated Queries from `genie/examples/curated_queries.json` and Trusted Assets from `genie/trusted_assets/`.
5. **Run Evaluation Suite**: Execute `genie/benchmarks/evaluation_suite.json` to verify test accuracy.
