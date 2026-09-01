# Governed Metric Catalog — Placewise Placement Intelligence

**Catalog:** `PLACEWISE`  
**Semantic Schema:** `PLACEWISE.SEMANTIC`  
**Governance Standard:** Unity Catalog Metric Views & Curated Semantic Objects  

---

## 1. Placement & Compensation Metrics

### 1.1 `placement_rate`
* **Business Definition**: Percentage of placement-eligible students who have secured a confirmed placement.
* **Formula**:
  ```sql
  ROUND(COUNT(DISTINCT CASE WHEN placed_flag = 1 THEN student_id END) * 100.0 
        / NULLIF(COUNT(DISTINCT CASE WHEN placement_status IN ('ELIGIBLE', 'ACTIVE', 'PLACED') THEN student_id END), 0), 2)
  ```
* **Grain**: Department, Degree Program, Cohort Graduation Year, Academic Year, Overall.
* **Numerator**: Distinct student count with `placed_flag = 1` or `placement_status = 'PLACED'`.
* **Denominator**: Distinct student count with `placement_status IN ('ELIGIBLE', 'ACTIVE', 'PLACED')`.
* **Filters**: Defaults to graduating cohort. Excludes `OPTED_OUT` and `NOT_STARTED` unless explicitly requested.
* **Null Behavior**: Returns `NULL` when denominator is 0.
* **Time Semantics**: Evaluated at student `graduation_year` or `placement_season`.
* **Source Object**: `semantic.genie_department_performance`, `semantic.genie_student_intelligence`.

### 1.2 `average_package` (CTC)
* **Business Definition**: Mean annual compensation (in LPA) for students with confirmed placements.
* **Formula**:
  ```sql
  ROUND(AVG(placed_ctc_lpa), 2)
  ```
* **Grain**: Department, Company, Industry, Role Family, Graduation Year.
* **Numerator**: Sum of `placed_ctc_lpa` for confirmed placements.
* **Denominator**: Count of confirmed placed students with non-null salary.
* **Filters**: `placed_flag = 1` and `placed_ctc_lpa > 0`.
* **Null Behavior**: Returns `NULL` if no placed students exist.
* **Time Semantics**: Date of placement confirmation or student graduation year.
* **Source Object**: `semantic.genie_department_performance`, `semantic.genie_company_intelligence`.

### 1.3 `median_package` (CTC)
* **Business Definition**: 50th percentile annual compensation (in LPA) for confirmed placements.
* **Formula**:
  ```sql
  ROUND(MEDIAN(placed_ctc_lpa), 2)
  ```
* **Grain**: Department, Company, Company Type, Industry, Graduation Year.
* **Source Object**: `semantic.genie_department_performance`, `semantic.genie_company_intelligence`.

---

## 2. Recruitment Funnel & Conversion Metrics

### 2.1 `application_to_interview_rate`
* **Business Definition**: Percentage of submitted applications that progressed to an interview round.
* **Formula**:
  ```sql
  ROUND(COUNT(DISTINCT CASE WHEN interviews_count > 0 THEN application_id END) * 100.0 
        / NULLIF(COUNT(DISTINCT application_id), 0), 2)
  ```
* **Grain**: Company, Job Posting, Department, Role Family.
* **Source Object**: `semantic.genie_company_intelligence`.

### 2.2 `interview_to_offer_rate`
* **Business Definition**: Percentage of interviewed applications that resulted in a formal job offer.
* **Formula**:
  ```sql
  ROUND(COUNT(DISTINCT offers_count) * 100.0 
        / NULLIF(COUNT(DISTINCT interviewed_applications), 0), 2)
  ```
* **Grain**: Company, Job Posting, Department, Role Family.
* **Source Object**: `semantic.genie_company_intelligence`.

### 2.3 `offer_acceptance_rate`
* **Business Definition**: Percentage of extended offers that were accepted by students.
* **Formula**:
  ```sql
  ROUND(COUNT(DISTINCT accepted_offers_count) * 100.0 
        / NULLIF(COUNT(DISTINCT offers_count), 0), 2)
  ```
* **Grain**: Company, Job Posting, Department, Industry.
* **Source Object**: `semantic.genie_company_intelligence`.

---

## 3. Student Readiness & Skill Metrics

### 3.1 `placement_readiness_score`
* **Business Definition**: Weighted deterministic composite score ($0–100$) reflecting overall student placement capability.
* **Formula**:
  ```sql
  ROUND(
      academic_score               * 0.20 +
      skill_score                  * 0.25 +
      internship_score             * 0.10 +
      project_score                * 0.10 +
      interview_score              * 0.20 +
      application_conversion_score * 0.15,
  2)
  ```
* **Grain**: Individual Student.
* **Source Object**: `semantic.genie_student_intelligence`.

### 3.2 `skill_supply_demand_gap`
* **Business Definition**: Disparity between the market demand ratio and student supply ratio for a specific skill.
* **Formula**:
  ```sql
  ROUND(market_demand_ratio - student_supply_ratio, 4)
  ```
* **Grain**: Skill, Skill Category.
* **Source Object**: `semantic.genie_skill_market`.

---

## 4. Trend & Year-over-Year (YoY) Metrics

### 4.1 `placement_rate_change_points`
* **Business Definition**: Net percentage point difference in department placement rate compared to the previous graduating batch.
* **Formula**:
  ```sql
  ROUND(placement_rate - LAG(placement_rate) OVER(PARTITION BY department_code ORDER BY graduation_year), 2)
  ```
* **Grain**: Department $	imes$ Graduation Year.
* **Source Object**: `semantic.genie_department_performance`.
