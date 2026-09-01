# Metric Definitions

### 1. Placement Rate
- **Business Definition**: Percentage of eligible students who received at least one job offer.
- **Formula**: `COUNT(DISTINCT CASE WHEN placement_status = 'Placed' THEN student_id END) * 100.0 / COUNT(DISTINCT student_id)`
- **Grain**: department | overall
- **Numerator**: Count of distinct placed students
- **Denominator**: Total count of distinct eligible students
- **Filters**: `is_eligible = TRUE` (if applicable)
- **Null Behavior**: Unplaced students count as 0 in numerator. Null placement status treated as unplaced.
- **Time Semantics**: Evaluated per `graduation_year`.
- **Source Table**: `gold_department_metrics`, `gold_student_metrics`

### 2. Average Package
- **Business Definition**: Average salary package (in LPA) among all accepted offers.
- **Formula**: `AVG(final_package_lpa)`
- **Grain**: department | company | overall
- **Numerator**: Sum of all `final_package_lpa`
- **Denominator**: Count of placements
- **Filters**: `final_package_lpa IS NOT NULL`
- **Null Behavior**: Null packages are ignored in AVG calculation.
- **Time Semantics**: Filterable by `offer_date` or `graduation_year`.
- **Source Table**: `silver_placements`

### 3. Median Package
- **Business Definition**: The middle salary package value when sorted.
- **Formula**: `percentile_cont(0.5) WITHIN GROUP (ORDER BY final_package_lpa)`
- **Grain**: department | overall
- **Numerator**: N/A
- **Denominator**: N/A
- **Filters**: None
- **Null Behavior**: Ignores nulls.
- **Time Semantics**: Filterable by `graduation_year`.
- **Source Table**: `silver_placements`

### 4. Highest Package
- **Business Definition**: The maximum salary package offered in a given cohort.
- **Formula**: `MAX(final_package_lpa)`
- **Grain**: department | overall
- **Numerator**: N/A
- **Denominator**: N/A
- **Filters**: None
- **Null Behavior**: Ignores nulls.
- **Time Semantics**: Filterable by `graduation_year`.
- **Source Table**: `silver_placements`

### 5. Average Placement Readiness
- **Business Definition**: Average composite score indicating a student's readiness.
- **Formula**: `AVG(placement_readiness_score)`
- **Grain**: student | department
- **Numerator**: Sum of readiness scores
- **Denominator**: Count of students
- **Filters**: None
- **Null Behavior**: Null treated as 0 or ignored depending on context.
- **Time Semantics**: Current snapshot.
- **Source Table**: `gold_student_metrics`

### 6. Interview Conversion Rate
- **Business Definition**: Percentage of interviews attended that resulted in passing to the next round or offer.
- **Formula**: `SUM(CASE WHEN result = 'Pass' THEN 1 ELSE 0 END) * 100.0 / COUNT(interview_id)`
- **Grain**: student | company
- **Numerator**: Count of passed interviews
- **Denominator**: Total interviews attended
- **Filters**: None
- **Null Behavior**: Null results treated as fail/incomplete.
- **Time Semantics**: Filterable by interview date.
- **Source Table**: `silver_interviews`

### 7. Application Conversion Rate
- **Business Definition**: Percentage of job applications that result in at least a first-round interview.
- **Formula**: `COUNT(DISTINCT CASE WHEN status IN ('Shortlisted', 'Selected') THEN application_id END) * 100.0 / COUNT(DISTINCT application_id)`
- **Grain**: student | company
- **Numerator**: Count of shortlisted/selected applications
- **Denominator**: Total applications
- **Filters**: None
- **Null Behavior**: Null status treated as applied/rejected.
- **Time Semantics**: Based on `application_date`.
- **Source Table**: `silver_applications`

### 8. Offer Acceptance Rate
- **Business Definition**: Percentage of final offers extended by companies that are accepted by students.
- **Formula**: `COUNT(placement_id) * 100.0 / COUNT(offer_extended_id)`
- **Grain**: company
- **Numerator**: Accepted offers (placements)
- **Denominator**: Extended offers
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Based on offer date.
- **Source Table**: `silver_placements`

### 9. Skill Gap Score (per student-job pair)
- **Business Definition**: Numeric representation of missing required skills for a specific job.
- **Formula**: `(Required Skills Count - Matched Skills Count) / Required Skills Count`
- **Grain**: student-job
- **Numerator**: Required - Matched
- **Denominator**: Required
- **Filters**: None
- **Null Behavior**: If 0 required skills, gap is 0.
- **Time Semantics**: Current snapshot.
- **Source Table**: `semantic_student_job_match`

### 10. Average Skill Match
- **Business Definition**: Average percentage of skills matched between a student's profile and applied jobs.
- **Formula**: `AVG(matched_skills_count * 100.0 / required_skills_count)`
- **Grain**: student | department
- **Numerator**: N/A
- **Denominator**: N/A
- **Filters**: `required_skills_count > 0`
- **Null Behavior**: Ignored if no skills required.
- **Time Semantics**: Current snapshot.
- **Source Table**: `semantic_student_job_match`

### 11. Company Hiring Count
- **Business Definition**: Total number of students hired by a specific company.
- **Formula**: `COUNT(DISTINCT student_id)`
- **Grain**: company
- **Numerator**: Count of students
- **Denominator**: 1
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Filterable by `offer_date`.
- **Source Table**: `silver_placements`

### 12. Student Application Count
- **Business Definition**: Number of jobs a student has applied to.
- **Formula**: `COUNT(application_id)`
- **Grain**: student
- **Numerator**: Count of applications
- **Denominator**: 1
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Filterable by `application_date`.
- **Source Table**: `silver_applications`

### 13. Placement Count
- **Business Definition**: Total number of placements (offers accepted) across the institution.
- **Formula**: `COUNT(placement_id)`
- **Grain**: overall | department
- **Numerator**: Count of placements
- **Denominator**: 1
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Filterable by `offer_date`.
- **Source Table**: `silver_placements`

### 14. Internship Conversion Rate
- **Business Definition**: Percentage of students who completed an internship at a company and received a full-time offer from the same company.
- **Formula**: `COUNT(DISTINCT CASE WHEN has_internship = TRUE AND p.company_id = i.company_id THEN p.student_id END) * 100.0 / COUNT(DISTINCT CASE WHEN has_internship = TRUE THEN i.student_id END)`
- **Grain**: company | overall
- **Numerator**: Interns converted to full-time
- **Denominator**: Total interns
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Filterable by cohort year.
- **Source Table**: `silver_placements` joined with `silver_internships`

### 15. Average Interview Score
- **Business Definition**: Average score achieved by a student across all interview rounds.
- **Formula**: `AVG(score)`
- **Grain**: student
- **Numerator**: Sum of interview scores
- **Denominator**: Count of scored interviews
- **Filters**: `score IS NOT NULL`
- **Null Behavior**: Null scores ignored.
- **Time Semantics**: Filterable by interview date.
- **Source Table**: `silver_interviews`

### 16. Job Posting Demand
- **Business Definition**: Number of applications received per job posting.
- **Formula**: `COUNT(application_id) / COUNT(DISTINCT job_id)`
- **Grain**: job | company
- **Numerator**: Total applications
- **Denominator**: Total job postings
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Filterable by posting date.
- **Source Table**: `silver_applications`

### 17. Skill Demand
- **Business Definition**: Number of job postings requiring a specific skill.
- **Formula**: `COUNT(DISTINCT job_id)`
- **Grain**: skill
- **Numerator**: Count of jobs
- **Denominator**: 1
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Filterable by posting date.
- **Source Table**: `silver_job_skills`

### 18. Department Placement Rate
- **Business Definition**: Placement Rate calculated at the department level.
- **Formula**: Same as Placement Rate.
- **Grain**: department
- **Numerator**: Placed students in dept
- **Denominator**: Total students in dept
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Filterable by `graduation_year`.
- **Source Table**: `gold_department_metrics`

### 19. Role Placement Rate
- **Business Definition**: Percentage of applications for a specific role title that result in placement.
- **Formula**: `COUNT(placement_id) * 100.0 / COUNT(application_id)`
- **Grain**: role_title
- **Numerator**: Placements for role
- **Denominator**: Applications for role
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Filterable by year.
- **Source Table**: `silver_applications` joined with `silver_placements`

### 20. Company Selection Rate
- **Business Definition**: Percentage of applicants to a company who are ultimately selected (placed).
- **Formula**: `COUNT(DISTINCT placement_id) * 100.0 / COUNT(DISTINCT application_id)`
- **Grain**: company
- **Numerator**: Placements at company
- **Denominator**: Applications to company
- **Filters**: None
- **Null Behavior**: N/A
- **Time Semantics**: Filterable by year.
- **Source Table**: `silver_applications` joined with `silver_placements`

### Component Scores (Sub-components)
- **academic_score**: Normalized CGPA (e.g., `cgpa * 10`).
- **skill_score**: Based on number of certified high-demand skills.
- **internship_score**: Points based on duration and tier of internship company.
- **project_score**: Points based on number and complexity of academic projects.
- **interview_score**: Normalized average of mock/real interview scores.
- **application_conversion_score**: Student's Application Conversion Rate relative to cohort average.
- **placement_readiness_score**: Weighted average of the above components (e.g., 30% academic, 30% skills, 20% interview, 10% internship, 10% projects).
