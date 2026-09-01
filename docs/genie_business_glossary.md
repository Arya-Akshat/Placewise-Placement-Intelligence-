# Placewise Genie Business Glossary & Semantic Dictionary

**Version:** 2.0  
**Scope:** Natural Language Understanding & Entity Mapping for Databricks Genie  

---

## 1. Core Placement Terminology & Strict Semantics

To prevent Genie from hallucinating business logic, the following canonical business definitions and synonyms are governed across Unity Catalog and Genie prompt contexts:

### 1.1 Placement & Offers
* **`placed` / `placement`**:
  * **Canonical Definition**: A student who has received a formal offer and has a confirmed, finalized record in `silver.placements` / `gold.student_placement_profile` with `placed_flag = 1`.
  * **Synonyms**: *got job*, *hired student*, *placed student*, *successfully recruited*.
  * **Critical Distinction**: An `OFFER` is **NOT** a placement. An `ACCEPTED OFFER` is a prerequisite, but only finalized placement records count toward placement statistics.
* **`placement rate`**:
  * **Canonical Definition**: Percentage of placement-eligible students who obtained a confirmed placement:
    $$\text{Placement Rate} = \frac{\text{Placed Students}}{\text{Eligible Students}} \times 100$$
  * **Synonyms**: *placement percentage*, *placement ratio*, *hiring percentage by branch*.
  * **Eligible Population Rule**: `placement_status IN ('ELIGIBLE', 'ACTIVE', 'PLACED')`. Excludes students who opted out for higher studies or are ineligible due to backlogs.
* **`package` / `compensation`**:
  * **Canonical Definition**: Annual Cost to Company (CTC) represented in **LPA (Lakhs Per Annum)**.
  * **Synonyms**: *CTC*, *salary*, *compensation*, *package in LPA*, *annual pay*.
  * **Unit**: INR Lakhs per year (e.g. `12.5` means ₹12,50,000 per annum).

### 1.2 Selection Funnel Stages
* **`application`**: A formal submission by an eligible student to a specific job posting.
* **`shortlist`**: Candidate selection post-resume screening or initial online assessment.
* **`interview`**: Evaluated technical, managerial, or HR interview round.
* **`interview conversion rate`**:
  * **Canonical Definition**: Percentage of interviewed candidates who received a formal offer:
    $$\text{Interview to Offer Rate} = \frac{\text{Offers Extended}}{\text{Interviewed Applications}} \times 100$$
  * **Synonyms**: *interview clearance rate*, *interview-to-offer percentage*.
* **`offer acceptance rate`**:
  * **Canonical Definition**: Percentage of extended offers that were accepted by students:
    $$\text{Offer Acceptance Rate} = \frac{\text{Accepted Offers}}{\text{Total Extended Offers}} \times 100$$

### 1.3 Readiness & Skill Metrics
* **`placement readiness score`**:
  * **Canonical Definition**: A governed deterministic composite index (0–100) combining Academic (20%), Skill (25%), Internship (10%), Project (10%), Interview (20%), and Application Conversion (15%) scores.
  * **Synonyms**: *readiness*, *student readiness*, *employability score*, *placement index*.
  * **Important Distinction**: This is an **analytical readiness index**, NOT a machine learning predicted probability.
* **`readiness band`**:
  * `VERY_HIGH` ($\ge 90.0$), `HIGH` ($75.0 - 89.99$), `MODERATE` ($60.0 - 74.99$), `LOW` ($40.0 - 59.99$), `VERY_LOW` ($< 40.0$).
* **`skill gap` / `skill match`**:
  * **`skill match percentage`**: Weighted percentage of required skills possessed by the student ($0 - 100\%$).
  * **`skill gap percentage`**: $100 - \text{skill match percentage}$. Weighted deficit against role requirements.

---

## 2. Priority Prompt Matching Columns

The following columns have Prompt Matching enabled in Databricks Genie to allow users to use natural naming without exact ID lookups:

| Table / Object | Column Name | Sample Natural Language Prompt Values | Prompt Matching Priority |
|---|---|---|---|
| `semantic.genie_department_performance` | `department_code` | "CSE", "ECE", "ME", "CE", "AIML", "IT", "EEE", "CH" | **CRITICAL** |
| `semantic.genie_department_performance` | `department_name` | "Computer Science", "Mechanical Engineering", "Electrical" | **HIGH** |
| `semantic.genie_company_intelligence` | `company_name` | "Oracle", "Microsoft", "Google", "Ring Central", "Wipro", "TCS" | **CRITICAL** |
| `semantic.genie_company_intelligence` | `industry` | "Technology", "Fintech", "Banking", "Consulting", "IT Services" | **HIGH** |
| `semantic.genie_company_intelligence` | `company_type` | "PRODUCT", "SERVICES", "STARTUP", "CONSULTING", "BANKING" | **HIGH** |
| `semantic.genie_student_intelligence` | `graduation_year` | 2023, 2024, 2025, 2026 | **CRITICAL** |
| `semantic.genie_student_intelligence` | `preferred_role` | "Software Engineering", "Data Engineering", "Machine Learning" | **HIGH** |
| `semantic.genie_student_intelligence` | `readiness_band` | "VERY_HIGH", "HIGH", "MODERATE", "LOW", "VERY_LOW" | **HIGH** |
| `semantic.genie_student_intelligence` | `placement_status` | "PLACED", "ELIGIBLE", "ACTIVE", "OPTED_OUT", "NOT_STARTED" | **CRITICAL** |
| `semantic.genie_skill_market` | `skill_name` | "Python", "SQL", "Spark", "AWS", "Docker", "Communication" | **CRITICAL** |
| `semantic.genie_skill_market` | `skill_category` | "Programming", "Database", "Cloud", "Big Data", "Soft Skills" | **HIGH** |
| `semantic.genie_student_job_match` | `candidate_fit_band` | "EXCELLENT", "STRONG", "GOOD", "FAIR", "POOR" | **HIGH** |

---

## 3. Curated Column Metadata & Semantic Definitions

### 3.1 `semantic.genie_student_intelligence`
* `student_id`: Unique surrogate key for student (e.g. `stu_e3b0c44298`).
* `cgpa`: Cumulative Grade Point Average on a 0.0 to 10.0 scale.
* `academic_score`: Academic component (0–100) combining CGPA (70%), 12th/Semester % (20%), and Attendance (10%).
* `skill_score`: Weighted proficiency across technical (1.0), tool (0.8), and soft (0.5) skills (0–100).
* `placement_readiness_score`: Composite readiness index ($0–100$).
* `placed_flag`: Binary indicator ($1 =$ Confirmed placement, $0 =$ Not placed).
* `placed_ctc_lpa`: Finalized placement salary package in Lakhs Per Annum (LPA).
* `unplaced_eligible_flag`: Boolean flag indicating students who are eligible/active but have not received a confirmed placement.
* `strong_academic_weak_interview_flag`: Boolean indicator identifying high-academic students (score $\ge 75$) with weak interview conversion ($< 50$).

### 3.2 `semantic.genie_company_intelligence`
* `company_id`: Unique identifier for employer.
* `job_postings_count`: Distinct number of campus drives / job postings published.
* `openings_count`: Total declared hiring openings.
* `placements_count`: Total distinct students hired.
* `average_ctc_lpa`: Mean finalized CTC offered to placed students.
* `hiring_selectivity_score`: $100 - (\text{Offers} / \text{Applications} \times 100)$ representing selection rigor ($0–100$).
* `company_package_position`: Qualitative tier (`TOP_DECILE`, `ABOVE_MEDIAN`, `AROUND_MEDIAN`, `BELOW_MEDIAN`).

### 3.3 `semantic.genie_department_performance`
* `department_code`: Academic department acronym (`CSE`, `ECE`, etc.).
* `graduation_year`: Graduating batch year ($2023, 2024, 2025, 2026$).
* `placement_rate`: Percentage of eligible students placed ($0.0 - 100.0\%$).
* `placement_rate_yoy`: Previous cohort's placement rate for year-over-year comparison.
* `placement_rate_change_points`: Year-over-year percentage point increase/decrease.
* `rank_within_year`: Department rank by placement rate within the graduation batch.

### 3.4 `semantic.genie_skill_market`
* `skill_name`: Canonical skill name (e.g. `Python`, `Spark`, `React`).
* `job_posting_count`: Total campus job postings requiring this skill.
* `students_with_skill_count`: Total students possessing verified proficiency.
* `student_supply_ratio`: Fraction of placement-eligible students possessing the skill ($0.0 - 1.0$).
* `market_demand_ratio`: Fraction of campus job postings requiring the skill ($0.0 - 1.0$).
* `high_demand_low_supply_flag`: Boolean flag identifying critical campus skill deficits ($	ext{Demand} > 15\%$ and $	ext{Supply} < 35\%$).
