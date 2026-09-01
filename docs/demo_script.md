# Placewise Executive Demo Script & Presentation Flow

This script outlines the canonical 7-step live demonstration for institutional leadership, placement cell deans, and corporate recruiters.

---

### Step 1: Department Placement Benchmarking
* **User Prompt**: `"What is the placement rate for CSE in 2024?"`
* **Target Semantic View**: `placewise.semantic.genie_department_performance`
* **Expected UI**:
  - Assistant textual confirmation: *"CSE placement rate for the 2024 graduating cohort was 51.49%..."*
  - Headline KPI Cards: Placement Rate (`51.49%`), Placed Students ($1,159$), Eligible ($2,251$), Average CTC (₹8.92 LPA).
  - Detailed department benchmark table.
* **Audience Takeaway**: Explicit governed definitions (placed eligible students / total eligible students) eliminate spreadsheet discrepancies.

---

### Step 2: Multi-Turn Comparative Analytics
* **User Prompt**: `"How does that compare with ECE?"`
* **Expected UI**:
  - Context retention within the same conversation session without repeating the 2024 batch filter.
  - Comparative Bar Chart (`<PlacementBarChart />`): CSE ($51.49\%$) vs ECE ($48.86\%$).
* **Audience Takeaway**: Natural follow-ups preserve cohort context seamlessly.

---

### Step 3: Recruiter Hiring Analytics
* **User Prompt**: `"Which companies hired the most students?"`
* **Target Semantic View**: `placewise.semantic.genie_company_intelligence`
* **Expected UI**:
  - Top 10 employer ranking by placement count.
  - Interactive table with CTC ranges and interview-to-offer clearance rates.
* **Audience Takeaway**: Segregated aggregation prevents join row multiplication.

---

### Step 4: Skill Market & Supply-Demand Gaps
* **User Prompt**: `"What skills are in highest demand?"`
* **Target Semantic View**: `placewise.semantic.genie_skill_market`
* **Expected UI**:
  - Recruiter demand ranking vs campus student proficiency.
  - High-demand low-supply badges for critical technology gaps (e.g. PySpark, Kubernetes).
* **Audience Takeaway**: Actionable curriculum feedback based on real job posting requirements.

---

### Step 5: Unplaced Candidate Discovery
* **User Prompt**: `"Show high-readiness students without offers."`
* **Target Semantic View**: `placewise.semantic.genie_student_intelligence`
* **Expected UI**:
  - Filtered candidate table ranked by `placement_readiness_score DESC`.
  - Academic scores, verified technical skill counts, and zero offers.
* **Audience Takeaway**: Placement cells can intervene proactively to support capable but unoffered students.

---

### Step 6: Candidate Matching Engine
* **User Prompt**: `"Find strong candidates for Data Engineering."`
* **Target Semantic View**: `placewise.semantic.genie_student_job_match`
* **Expected UI**:
  - Candidate recommendation matrix with Candidate Fit Band, Skill Match %, and Readiness Score.
  - Strict enforcement of mandatory eligibility gates.
* **Audience Takeaway**: Instant recruiter shortlisting without manual resume filtering.

---

### Step 7: Agent Mode Multi-Step Reasoning
* **User Prompt**: `"Why did Mechanical placement performance change?"`
* **Target Semantic View**: Multi-Object Decomposition
* **Expected UI**:
  - `<AgentAnalysis />` accordion with Executive Summary, 4 Key Observed Drivers, and Evidence Cards.
  - Strictly descriptive, correlational insights without unsupported causal assumptions.
* **Audience Takeaway**: Complex investigative questions broken down systematically across data domains.
