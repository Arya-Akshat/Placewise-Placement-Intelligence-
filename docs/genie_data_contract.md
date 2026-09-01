# Placewise Semantic Layer Data Contract

**Version:** 2.0  
**Status:** Certified & Governed  

---

## 1. Purpose & Backward Compatibility Guarantee

This data contract establishes the formal schema and behavioral guarantees provided by the `PLACEWISE.SEMANTIC` layer to Databricks Genie, downstream BI dashboards, and the React frontend.

When future institutional data replaces the synthetic data layer:
1. **Zero Genie Redesign**: All 5 `semantic.genie_*` objects maintain identical schema column names, data types, and grain definitions.
2. **Deterministic Mapping**: Ingestion pipelines map new source data into Silver, leaving Semantic view definitions untouched.

---

## 2. Schema Guarantees

### 2.1 `semantic.genie_student_intelligence`
* `student_id`: `STRING` (Primary Key, Non-Null)
* `department_code`: `STRING` (`CSE`, `ECE`, `ME`, etc.)
* `graduation_year`: `INT` ($2018 - 2030$)
* `cgpa`: `DOUBLE` ($0.0 - 10.0$)
* `placement_status`: `STRING` (`PLACED`, `ELIGIBLE`, `ACTIVE`, `OPTED_OUT`, `NOT_STARTED`)
* `placement_readiness_score`: `DOUBLE` ($0.0 - 100.0$)
* `readiness_band`: `STRING` (`VERY_HIGH`, `HIGH`, `MODERATE`, `LOW`, `VERY_LOW`)
* `placed_flag`: `INT` ($0$ or $1$)
* `placed_ctc_lpa`: `DOUBLE` (Null if unplaced, positive float if placed)

### 2.2 `semantic.genie_company_intelligence`
* `company_id`: `STRING` (Primary Key, Non-Null)
* `company_name`: `STRING` (Non-Null)
* `industry`: `STRING`
* `company_type`: `STRING` (`PRODUCT`, `SERVICES`, `STARTUP`, `CONSULTING`, `BANKING`, `CORE`)
* `placements_count`: `BIGINT` ($\ge 0$)
* `average_ctc_lpa`: `DOUBLE` ($\ge 0$)

### 2.3 `semantic.genie_department_performance`
* `department_code`: `STRING` (Non-Null)
* `graduation_year`: `INT` (Non-Null)
* `placement_rate`: `DOUBLE` ($0.0 - 100.0$)
* `placement_rate_yoy`: `DOUBLE` ($0.0 - 100.0$ or Null for first cohort)
* `rank_within_year`: `BIGINT` ($1 - N$)

---

## 3. SLA & Quality Invariants
* **Orphan Records**: $0$ orphan foreign keys allowed in Semantic views.
* **Divide-by-Zero Safety**: All division operations must use `NULLIF(denominator, 0)`.
* **Grain Integrity**: Aggregations at department, company, and skill grains must be isolated in independent CTEs to prevent row multiplication.
