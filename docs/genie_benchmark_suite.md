# Placewise Databricks Genie Benchmark Suite

**Total Benchmarks:** 18 Certified Benchmark Queries  
**Target Schemas:** `PLACEWISE.SEMANTIC`  
**Evaluation Standard:** 100% Deterministic SQL Grounding  

---

## 1. Benchmark Suite Categories

The benchmark suite rigorously tests natural-language to SQL translation across 9 core categories:
1. **Metric Accuracy**: Ensures exact calculation of placement rates, CTC averages/medians, and count metrics.
2. **Filter Accuracy**: Validates compound boolean filters (e.g. readiness $> 80$ AND offers $= 0$).
3. **Join Accuracy**: Verifies that multi-table relationships maintain correct grain without row multiplication.
4. **Time Accuracy**: Ensures proper filtering by graduation year, academic year, and placement season.
5. **Ranking Accuracy**: Validates deterministic ranking of candidates, departments, and employers.
6. **Skill Analytics**: Tests demand vs supply ratio calculations and gap rankings.
7. **Funnel Analytics**: Verifies stage conversion rates and pipeline drop-off calculations.
8. **Multi-Step Reasoning (Agent Mode)**: Complex analytical decompositions (e.g. why department rates changed).
9. **Clarification Behavior**: Prompts requiring Genie to ask clarifying questions before execution.

---

## 2. Benchmark Definitions & Paraphrase Coverage

| Benchmark ID | Category | Primary Natural Language Question | Paraphrase Variations | Target Semantic Object | Expected Metric |
|---|---|---|---|---|---|
| **BM-001** | Metric Accuracy | **"What is the placement rate for CSE in the 2024 batch?"** | <br>• What percent of eligible CSE students got placed in 2024?<br>• CSE 2024 placement percentage?<br>• How many CSE students were placed out of the eligible pool in 2024? | `semantic.genie_department_performance` | `placement_rate` |
| **BM-002** | Metric Accuracy | **"What is the average package for students placed in product companies?"** | <br>• Average CTC for product company placements?<br>• Mean salary package in product companies?<br>• What do product companies pay on average? | `semantic.genie_company_intelligence` | `average_ctc_lpa` |
| **BM-003** | Metric Accuracy | **"What is the median package for ECE graduates?"** | <br>• Median CTC for ECE?<br>• 50th percentile salary for ECE placed students?<br>• ECE median package in 2024? | `semantic.genie_department_performance` | `median_ctc_lpa` |
| **BM-004** | Metric Accuracy | **"What is the highest package offered across all departments in 2024?"** | <br>• Maximum CTC in 2024?<br>• Top salary package this year?<br>• Highest package placed student in 2024? | `semantic.genie_department_performance` | `highest_ctc_lpa` |
| **BM-005** | Metric Accuracy | **"How many total students are placed in the 2024 graduating class?"** | <br>• Total placed students in 2024?<br>• 2024 batch placement count?<br>• Number of placements in 2024? | `semantic.genie_department_performance` | `placed_students` |
| **BM-006** | Filter Accuracy | **"Show all Computer Science students with readiness above 80 who have not received an offer."** | <br>• CSE students with readiness > 80 and no offers?<br>• Unplaced high readiness CSE candidates?<br>• Who in CSE has high readiness but 0 offers? | `semantic.genie_student_intelligence` | `placement_readiness_score` |
| **BM-007** | Filter Accuracy | **"Show students with strong academics (CGPA >= 8.5) but weak interview conversion."** | <br>• High CGPA students who failed interviews?<br>• Students with CGPA >= 8.5 and interview score < 50?<br>• Academic toppers with weak interview performance? | `semantic.genie_student_intelligence` | `strong_academic_weak_interview_flag` |
| **BM-008** | Filter Accuracy | **"Which students have completed at least 2 internships but are still unplaced?"** | <br>• Unplaced students with 2+ internships?<br>• Experienced students without placement?<br>• Students with multiple internships and no placement? | `semantic.genie_student_intelligence` | `internship_count` |
| **BM-009** | Company Analytics | **"Which companies hired the most students?"** | <br>• Top hiring companies by headcount?<br>• Who recruited the most students?<br>• Companies with highest placements? | `semantic.genie_company_intelligence` | `placements_count` |
| **BM-010** | Company Analytics | **"Which companies have the highest interview-to-offer conversion rate?"** | <br>• Best interview to offer ratio companies?<br>• Where is interview clearance rate highest?<br>• Top companies by interview conversion? | `semantic.genie_company_intelligence` | `interview_to_offer_rate` |
| **BM-011** | Company Analytics | **"Which companies have high declared openings but low placement conversion?"** | <br>• Companies with many openings but few hires?<br>• Low conversion high opening companies?<br>• Where did openings not translate to placements? | `semantic.genie_company_intelligence` | `hiring_conversion_score` |
| **BM-012** | Skill Analytics | **"What are the top 10 most demanded skills by recruiters?"** | <br>• Most required skills in job postings?<br>• Top recruiter skill requirements?<br>• Which skills appear most in campus drives? | `semantic.genie_skill_market` | `job_posting_count` |
| **BM-013** | Skill Analytics | **"Which skills have high market demand but low student supply?"** | <br>• High demand low supply skills?<br>• Where is the largest skill deficit on campus?<br>• Skills required by companies but lacking among students? | `semantic.genie_skill_market` | `high_demand_low_supply_flag` |
| **BM-014** | Skill Analytics | **"What is the average skill gap for SQL and Python?"** | <br>• Proficiency gap in Python and SQL?<br>• How big is the deficit for Python and SQL?<br>• Average required vs student score for Python and SQL? | `semantic.genie_skill_market` | `average_skill_gap` |
| **BM-015** | Trend Analytics | **"Compare CSE placement rate across 2023 and 2024 graduating batches."** | <br>• CSE placement rate YoY change?<br>• Did CSE improve from 2023 to 2024?<br>• CSE placement rate trend 2023 vs 2024? | `semantic.genie_department_performance` | `placement_rate_change_points` |
| **BM-016** | Trend Analytics | **"Which departments improved their placement rate compared to last year?"** | <br>• Which branches increased placement percentage YoY?<br>• Departments with positive placement growth?<br>• Top improving departments in 2024? | `semantic.genie_department_performance` | `placement_rate_change_points` |
| **BM-017** | Candidate Matching | **"Show top software engineering candidates by readiness and technical skill."** | <br>• Best software engineering students?<br>• Top software developer candidates?<br>• Highest readiness students for Software Engineering? | `semantic.genie_student_intelligence` | `placement_readiness_score` |
| **BM-018** | Candidate Matching | **"Show candidates in the VERY_HIGH readiness band."** | <br>• Students with readiness_band = VERY_HIGH?<br>• Top tier placement readiness students?<br>• Who is in the top readiness bracket? | `semantic.genie_student_intelligence` | `readiness_band` |
