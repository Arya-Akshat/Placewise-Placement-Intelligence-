# Genie Question Test Suite

This document contains 40+ natural language questions grouped by domain to test the Genie natural language interface.

## 1. Student Analytics (10 questions)

#### Q1: Show students with placement readiness above 80
- **Domain**: Student Analytics
- **Required Tables**: gold.student_placement_profile
- **Required Joins**: None (self-contained)
- **Metric**: placement_readiness_score
- **Expected SQL**:
  ```sql
  SELECT student_id, full_name, department, cgpa, placement_readiness_score
  FROM placewise.gold.student_placement_profile
  WHERE placement_readiness_score > 80
  ORDER BY placement_readiness_score DESC;
  ```
- **Expected Answer Shape**: Table of students ranked by readiness

#### Q2: What is the average CGPA of placed students?
- **Domain**: Student Analytics
- **Required Tables**: gold.student_placement_profile
- **Required Joins**: None
- **Metric**: average cgpa
- **Expected SQL**:
  ```sql
  SELECT AVG(cgpa) as avg_cgpa
  FROM placewise.gold.student_placement_profile
  WHERE placement_status = 'PLACED';
  ```
- **Expected Answer Shape**: Single scalar value

#### Q3: Which students have a skill match over 90% for Python?
- **Domain**: Student Analytics
- **Required Tables**: gold.student_placement_profile, silver.student_skills
- **Required Joins**: student_id
- **Metric**: skill proficiency
- **Expected SQL**:
  ```sql
  SELECT p.full_name
  FROM placewise.gold.student_placement_profile p
  JOIN placewise.silver.student_skills s ON p.student_id = s.student_id
  WHERE s.skill_name = 'Python' AND s.proficiency_score > 90;
  ```
- **Expected Answer Shape**: List of student names

#### Q4: List top 5 students in Computer Science by academic score.
- **Domain**: Student Analytics
- **Required Tables**: gold.student_placement_profile
- **Required Joins**: None
- **Metric**: academic_score
- **Expected SQL**:
  ```sql
  SELECT full_name, academic_score
  FROM placewise.gold.student_placement_profile
  WHERE department = 'Computer Science'
  ORDER BY academic_score DESC LIMIT 5;
  ```
- **Expected Answer Shape**: Table with 5 rows

#### Q5: How many students are eligible but not placed yet?
- **Domain**: Student Analytics
- **Required Tables**: gold.student_placement_profile
- **Required Joins**: None
- **Metric**: count of students
- **Expected SQL**:
  ```sql
  SELECT COUNT(*) as unplaced_eligible
  FROM placewise.gold.student_placement_profile
  WHERE placement_status = 'ELIGIBLE';
  ```
- **Expected Answer Shape**: Single scalar value

#### Q6: Show students with backlogs.
- **Domain**: Student Analytics
- **Required Tables**: silver.students
- **Required Joins**: None
- **Metric**: count of backlogs
- **Expected SQL**:
  ```sql
  SELECT full_name, backlogs
  FROM placewise.silver.students
  WHERE backlogs > 0;
  ```
- **Expected Answer Shape**: Table of students and backlog counts

#### Q7: What is the gender diversity among placed students?
- **Domain**: Student Analytics
- **Required Tables**: silver.students
- **Required Joins**: None
- **Metric**: grouping by gender
- **Expected SQL**:
  ```sql
  SELECT gender, COUNT(*) as count
  FROM placewise.silver.students
  WHERE placement_status = 'PLACED'
  GROUP BY gender;
  ```
- **Expected Answer Shape**: Aggregated table

#### Q8: Find students who applied to Google but didn't get shortlisted.
- **Domain**: Student Analytics
- **Required Tables**: silver.applications, silver.job_postings, silver.companies, silver.students
- **Required Joins**: application -> posting -> company, application -> student
- **Metric**: status check
- **Expected SQL**:
  ```sql
  SELECT s.full_name
  FROM placewise.silver.applications a
  JOIN placewise.silver.job_postings p ON a.job_posting_id = p.job_posting_id
  JOIN placewise.silver.companies c ON p.company_id = c.company_id
  JOIN placewise.silver.students s ON a.student_id = s.student_id
  WHERE c.name = 'Google' AND a.status = 'REJECTED_AT_RESUME';
  ```
- **Expected Answer Shape**: List of student names

#### Q9: Which students opted out of placements?
- **Domain**: Student Analytics
- **Required Tables**: silver.students
- **Required Joins**: None
- **Metric**: placement_status
- **Expected SQL**:
  ```sql
  SELECT full_name
  FROM placewise.silver.students
  WHERE placement_status = 'OPTED_OUT';
  ```
- **Expected Answer Shape**: List of student names

#### Q10: Show the distribution of 10th vs 12th percentages for students.
- **Domain**: Student Analytics
- **Required Tables**: silver.students
- **Required Joins**: None
- **Metric**: 10th and 12th marks
- **Expected SQL**:
  ```sql
  SELECT full_name, tenth_percentage, twelfth_percentage
  FROM placewise.silver.students;
  ```
- **Expected Answer Shape**: Table of percentage data

## 2. Company Analytics (7 questions)

#### Q11: Which company hired the most students?
- **Domain**: Company Analytics
- **Required Tables**: gold.company_hiring_profile
- **Required Joins**: None
- **Metric**: total_placements
- **Expected SQL**:
  ```sql
  SELECT company_name, total_placements
  FROM placewise.gold.company_hiring_profile
  ORDER BY total_placements DESC LIMIT 1;
  ```
- **Expected Answer Shape**: Single row table

#### Q12: Show companies with highest offer acceptance rates.
- **Domain**: Company Analytics
- **Required Tables**: gold.company_hiring_profile
- **Required Joins**: None
- **Metric**: offer_acceptance_rate
- **Expected SQL**:
  ```sql
  SELECT company_name, offer_acceptance_rate
  FROM placewise.gold.company_hiring_profile
  ORDER BY offer_acceptance_rate DESC;
  ```
- **Expected Answer Shape**: Table ordered by rate

#### Q13: What is the average CTC offered by Microsoft?
- **Domain**: Company Analytics
- **Required Tables**: gold.company_hiring_profile
- **Required Joins**: None
- **Metric**: average_ctc
- **Expected SQL**:
  ```sql
  SELECT average_ctc_offered
  FROM placewise.gold.company_hiring_profile
  WHERE company_name = 'Microsoft';
  ```
- **Expected Answer Shape**: Single scalar value

#### Q14: List tier 1 companies.
- **Domain**: Company Analytics
- **Required Tables**: silver.companies
- **Required Joins**: None
- **Metric**: company tier
- **Expected SQL**:
  ```sql
  SELECT name
  FROM placewise.silver.companies
  WHERE tier = 1;
  ```
- **Expected Answer Shape**: List of company names

#### Q15: Which companies visited campus in 2023?
- **Domain**: Company Analytics
- **Required Tables**: silver.job_postings, silver.companies
- **Required Joins**: posting -> company
- **Metric**: posting year
- **Expected SQL**:
  ```sql
  SELECT DISTINCT c.name
  FROM placewise.silver.companies c
  JOIN placewise.silver.job_postings p ON c.company_id = p.company_id
  WHERE YEAR(p.posting_date) = 2023;
  ```
- **Expected Answer Shape**: List of company names

#### Q16: Show companies that offered CTC > 20 LPA.
- **Domain**: Company Analytics
- **Required Tables**: silver.job_postings, silver.companies
- **Required Joins**: posting -> company
- **Metric**: max_ctc
- **Expected SQL**:
  ```sql
  SELECT DISTINCT c.name
  FROM placewise.silver.companies c
  JOIN placewise.silver.job_postings p ON c.company_id = p.company_id
  WHERE p.package_max_lpa > 20;
  ```
- **Expected Answer Shape**: List of company names

#### Q17: What are the most common required skills by top tier companies?
- **Domain**: Company Analytics
- **Required Tables**: silver.job_skills, silver.job_postings, silver.companies
- **Required Joins**: job_skills -> postings -> companies
- **Metric**: skill counts
- **Expected SQL**:
  ```sql
  SELECT js.skill_name, COUNT(*) as demand
  FROM placewise.silver.job_skills js
  JOIN placewise.silver.job_postings p ON js.job_posting_id = p.job_posting_id
  JOIN placewise.silver.companies c ON p.company_id = c.company_id
  WHERE c.tier = 1
  GROUP BY js.skill_name
  ORDER BY demand DESC;
  ```
- **Expected Answer Shape**: Table of skills and counts

## 3. Placement Analytics (5 questions)

#### Q18: What is the overall placement rate for the 2024 batch?
- **Domain**: Placement Analytics
- **Required Tables**: gold.department_metrics (or calculated from students)
- **Required Joins**: None
- **Metric**: placement_rate
- **Expected SQL**:
  ```sql
  SELECT (COUNT(CASE WHEN placement_status = 'PLACED' THEN 1 END) * 100.0 / 
          COUNT(CASE WHEN placement_status IN ('ELIGIBLE', 'ACTIVE', 'PLACED') THEN 1 END)) as rate
  FROM placewise.silver.students
  WHERE batch_year = 2024;
  ```
- **Expected Answer Shape**: Single percentage

#### Q19: What is the highest package offered this year?
- **Domain**: Placement Analytics
- **Required Tables**: silver.offers
- **Required Joins**: None
- **Metric**: max CTC
- **Expected SQL**:
  ```sql
  SELECT MAX(ctc_lpa) as highest_package
  FROM placewise.silver.offers
  WHERE YEAR(offer_date) = YEAR(CURRENT_DATE());
  ```
- **Expected Answer Shape**: Scalar value

#### Q20: Show average CTC by department.
- **Domain**: Placement Analytics
- **Required Tables**: gold.department_metrics
- **Required Joins**: None
- **Metric**: avg_ctc
- **Expected SQL**:
  ```sql
  SELECT department, average_ctc
  FROM placewise.gold.department_metrics;
  ```
- **Expected Answer Shape**: Table of departments and average CTCs

#### Q21: What is the interview to offer conversion rate?
- **Domain**: Placement Analytics
- **Required Tables**: gold.funnel_metrics
- **Required Joins**: None
- **Metric**: interview_to_offer_rate
- **Expected SQL**:
  ```sql
  SELECT (SUM(offers_count) * 100.0 / NULLIF(SUM(interviews_count), 0)) as rate
  FROM placewise.gold.funnel_metrics;
  ```
- **Expected Answer Shape**: Scalar percentage

#### Q22: Find the median package across all placements.
- **Domain**: Placement Analytics
- **Required Tables**: silver.offers
- **Required Joins**: None
- **Metric**: median CTC
- **Expected SQL**:
  ```sql
  SELECT percentile_approx(ctc_lpa, 0.5) as median_ctc
  FROM placewise.silver.offers;
  ```
- **Expected Answer Shape**: Scalar value

## 4. Department Analytics (5 questions)

#### Q23: Which department has the highest placement rate?
- **Domain**: Department Analytics
- **Required Tables**: gold.department_metrics
- **Required Joins**: None
- **Metric**: placement_rate
- **Expected SQL**:
  ```sql
  SELECT department, placement_rate
  FROM placewise.gold.department_metrics
  ORDER BY placement_rate DESC LIMIT 1;
  ```
- **Expected Answer Shape**: Single row table

#### Q24: Compare average CGPA of CS vs Mechanical.
- **Domain**: Department Analytics
- **Required Tables**: silver.students
- **Required Joins**: None
- **Metric**: avg cgpa
- **Expected SQL**:
  ```sql
  SELECT department, AVG(cgpa)
  FROM placewise.silver.students
  WHERE department IN ('Computer Science', 'Mechanical Engineering')
  GROUP BY department;
  ```
- **Expected Answer Shape**: Table with 2 rows

#### Q25: Total unplaced students in Electronics.
- **Domain**: Department Analytics
- **Required Tables**: silver.students
- **Required Joins**: None
- **Metric**: count unplaced
- **Expected SQL**:
  ```sql
  SELECT COUNT(*)
  FROM placewise.silver.students
  WHERE department LIKE 'Electronics%' AND placement_status = 'ELIGIBLE';
  ```
- **Expected Answer Shape**: Scalar value

#### Q26: Department wise total job offers.
- **Domain**: Department Analytics
- **Required Tables**: silver.offers, silver.applications, silver.students
- **Required Joins**: offers -> applications -> students
- **Metric**: count of offers
- **Expected SQL**:
  ```sql
  SELECT s.department, COUNT(o.id) as offer_count
  FROM placewise.silver.offers o
  JOIN placewise.silver.applications a ON o.application_id = a.id
  JOIN placewise.silver.students s ON a.student_id = s.student_id
  GROUP BY s.department;
  ```
- **Expected Answer Shape**: Aggregated table

#### Q27: Top hiring company for Civil department.
- **Domain**: Department Analytics
- **Required Tables**: silver.placements, silver.offers, silver.applications, silver.job_postings, silver.companies, silver.students
- **Required Joins**: Multiple
- **Metric**: count placements
- **Expected SQL**:
  ```sql
  SELECT c.name, COUNT(*) as hires
  FROM placewise.silver.placements pl
  JOIN placewise.silver.offers o ON pl.offer_id = o.id
  JOIN placewise.silver.applications a ON o.application_id = a.id
  JOIN placewise.silver.students s ON a.student_id = s.student_id
  JOIN placewise.silver.job_postings p ON a.job_posting_id = p.job_posting_id
  JOIN placewise.silver.companies c ON p.company_id = c.company_id
  WHERE s.department = 'Civil Engineering'
  GROUP BY c.name
  ORDER BY hires DESC LIMIT 1;
  ```
- **Expected Answer Shape**: Single row

## 5. Skill Analytics (5 questions)

#### Q28: What is the most in-demand skill?
- **Domain**: Skill Analytics
- **Required Tables**: silver.job_skills
- **Required Joins**: None
- **Metric**: skill frequency
- **Expected SQL**:
  ```sql
  SELECT skill_name, COUNT(*) as demand
  FROM placewise.silver.job_skills
  GROUP BY skill_name
  ORDER BY demand DESC LIMIT 1;
  ```
- **Expected Answer Shape**: Single row

#### Q29: Average skill gap for Data Science roles.
- **Domain**: Skill Analytics
- **Required Tables**: gold.skill_gap_analysis
- **Required Joins**: None
- **Metric**: avg_gap
- **Expected SQL**:
  ```sql
  SELECT AVG(gap_percentage)
  FROM placewise.gold.skill_gap_analysis
  WHERE role = 'Data Scientist';
  ```
- **Expected Answer Shape**: Scalar value

#### Q30: Students with AWS certification.
- **Domain**: Skill Analytics
- **Required Tables**: silver.student_skills, silver.students
- **Required Joins**: student_skills -> students
- **Metric**: skill existence
- **Expected SQL**:
  ```sql
  SELECT s.full_name
  FROM placewise.silver.student_skills sk
  JOIN placewise.silver.students s ON sk.student_id = s.student_id
  WHERE sk.skill_name = 'AWS';
  ```
- **Expected Answer Shape**: List of names

#### Q31: How many companies require React?
- **Domain**: Skill Analytics
- **Required Tables**: silver.job_skills, silver.job_postings
- **Required Joins**: job_skills -> postings
- **Metric**: count distinct companies
- **Expected SQL**:
  ```sql
  SELECT COUNT(DISTINCT p.company_id)
  FROM placewise.silver.job_skills js
  JOIN placewise.silver.job_postings p ON js.job_posting_id = p.job_posting_id
  WHERE js.skill_name = 'React';
  ```
- **Expected Answer Shape**: Scalar value

#### Q32: Distribution of Python proficiency scores.
- **Domain**: Skill Analytics
- **Required Tables**: silver.student_skills
- **Required Joins**: None
- **Metric**: histogram data
- **Expected SQL**:
  ```sql
  SELECT proficiency_score, COUNT(*)
  FROM placewise.silver.student_skills
  WHERE skill_name = 'Python'
  GROUP BY proficiency_score;
  ```
- **Expected Answer Shape**: Table for histogram

## 6. Application Funnel (4 questions)

#### Q33: Overall application to shortlist rate.
- **Domain**: Application Funnel
- **Required Tables**: gold.funnel_metrics
- **Required Joins**: None
- **Metric**: rate
- **Expected SQL**:
  ```sql
  SELECT (SUM(shortlists_count) * 100.0 / NULLIF(SUM(applications_count), 0))
  FROM placewise.gold.funnel_metrics;
  ```
- **Expected Answer Shape**: Scalar percentage

#### Q34: At which stage do most students get rejected by Amazon?
- **Domain**: Application Funnel
- **Required Tables**: silver.applications, silver.job_postings, silver.companies
- **Required Joins**: applications -> postings -> companies
- **Metric**: status counts
- **Expected SQL**:
  ```sql
  SELECT a.status, COUNT(*)
  FROM placewise.silver.applications a
  JOIN placewise.silver.job_postings p ON a.job_posting_id = p.job_posting_id
  JOIN placewise.silver.companies c ON p.company_id = c.company_id
  WHERE c.name = 'Amazon' AND a.status LIKE 'REJECTED%'
  GROUP BY a.status
  ORDER BY COUNT(*) DESC LIMIT 1;
  ```
- **Expected Answer Shape**: Single row string

#### Q35: How many interviews were scheduled last month?
- **Domain**: Application Funnel
- **Required Tables**: silver.interviews
- **Required Joins**: None
- **Metric**: count
- **Expected SQL**:
  ```sql
  SELECT COUNT(*)
  FROM placewise.silver.interviews
  WHERE MONTH(scheduled_at) = MONTH(CURRENT_DATE() - INTERVAL 1 MONTH);
  ```
- **Expected Answer Shape**: Scalar

#### Q36: Drop off rate between technical and HR interviews.
- **Domain**: Application Funnel
- **Required Tables**: silver.interviews
- **Required Joins**: None
- **Metric**: calculated rate
- **Expected SQL**:
  ```sql
  -- Assumes specific logic to track stages
  ```
- **Expected Answer Shape**: Percentage

## 7. Time-Series (3 questions)

#### Q37: Placement count trend over the last 5 years.
- **Domain**: Time-Series
- **Required Tables**: silver.placements
- **Required Joins**: None
- **Metric**: count by year
- **Expected SQL**:
  ```sql
  SELECT YEAR(placement_date), COUNT(*)
  FROM placewise.silver.placements
  GROUP BY YEAR(placement_date)
  ORDER BY YEAR(placement_date);
  ```
- **Expected Answer Shape**: Time series table

#### Q38: Average package growth over the last 3 years.
- **Domain**: Time-Series
- **Required Tables**: silver.offers
- **Required Joins**: None
- **Metric**: avg CTC by year
- **Expected SQL**:
  ```sql
  SELECT YEAR(offer_date), AVG(ctc_lpa)
  FROM placewise.silver.offers
  WHERE YEAR(offer_date) >= YEAR(CURRENT_DATE()) - 3
  GROUP BY YEAR(offer_date);
  ```
- **Expected Answer Shape**: Time series table

#### Q39: Monthly application volume for this season.
- **Domain**: Time-Series
- **Required Tables**: silver.applications
- **Required Joins**: None
- **Metric**: count by month
- **Expected SQL**:
  ```sql
  SELECT MONTH(application_date), COUNT(*)
  FROM placewise.silver.applications
  GROUP BY MONTH(application_date)
  ORDER BY MONTH(application_date);
  ```
- **Expected Answer Shape**: Time series table

## 8. Recruiter Discovery (4 questions)

#### Q40: Find top 10 students matching Software Engineer role requirements.
- **Domain**: Recruiter Discovery
- **Required Tables**: gold.student_placement_profile, gold.skill_match
- **Required Joins**: profile -> match
- **Metric**: match_percentage
- **Expected SQL**:
  ```sql
  SELECT p.full_name, m.match_percentage
  FROM placewise.gold.student_placement_profile p
  JOIN placewise.gold.skill_match m ON p.student_id = m.student_id
  WHERE m.role = 'Software Engineer'
  ORDER BY m.match_percentage DESC LIMIT 10;
  ```
- **Expected Answer Shape**: Table

#### Q41: Show students with >8 CGPA, knows Java, and not placed.
- **Domain**: Recruiter Discovery
- **Required Tables**: silver.students, silver.student_skills
- **Required Joins**: students -> skills
- **Metric**: filter
- **Expected SQL**:
  ```sql
  SELECT s.full_name
  FROM placewise.silver.students s
  JOIN placewise.silver.student_skills sk ON s.student_id = sk.student_id
  WHERE s.cgpa > 8 AND sk.skill_name = 'Java' AND s.placement_status = 'ELIGIBLE';
  ```
- **Expected Answer Shape**: List of names

#### Q42: List students who have completed an internship.
- **Domain**: Recruiter Discovery
- **Required Tables**: silver.student_experiences (assuming table exists) or profile
- **Required Joins**: None
- **Metric**: experience check
- **Expected SQL**:
  ```sql
  -- depends on schema, e.g.
  SELECT full_name FROM placewise.gold.student_placement_profile WHERE internship_score > 0;
  ```
- **Expected Answer Shape**: List of names

#### Q43: Find students with high readiness score but low interview conversions.
- **Domain**: Recruiter Discovery
- **Required Tables**: gold.student_placement_profile
- **Required Joins**: None
- **Metric**: readiness vs conversion
- **Expected SQL**:
  ```sql
  SELECT full_name
  FROM placewise.gold.student_placement_profile
  WHERE placement_readiness_score > 80 AND interview_score < 40;
  ```
- **Expected Answer Shape**: List of names

## 9. Cross-Domain (4 questions)

#### Q44: Does high CGPA correlate with higher CTC?
- **Domain**: Cross-Domain
- **Required Tables**: silver.students, silver.offers, silver.applications
- **Required Joins**: students -> applications -> offers
- **Metric**: correlation
- **Expected SQL**:
  ```sql
  SELECT corr(s.cgpa, o.ctc_lpa)
  FROM placewise.silver.students s
  JOIN placewise.silver.applications a ON s.student_id = a.student_id
  JOIN placewise.silver.offers o ON a.id = o.application_id;
  ```
- **Expected Answer Shape**: Scalar correlation coefficient

#### Q45: Are students from Tier 1 cities more likely to get Tier 1 companies?
- **Domain**: Cross-Domain
- **Required Tables**: silver.students, silver.companies, silver.applications
- **Required Joins**: students -> apps -> postings -> companies
- **Metric**: cross-tabulation
- **Expected SQL**:
  ```sql
  -- complex query grouping by student city tier and company tier
  ```
- **Expected Answer Shape**: Cross-tab table

#### Q46: Which department has the most diverse skill set?
- **Domain**: Cross-Domain
- **Required Tables**: silver.students, silver.student_skills
- **Required Joins**: students -> skills
- **Metric**: distinct skills per dept
- **Expected SQL**:
  ```sql
  SELECT s.department, COUNT(DISTINCT sk.skill_name)
  FROM placewise.silver.students s
  JOIN placewise.silver.student_skills sk ON s.student_id = sk.student_id
  GROUP BY s.department;
  ```
- **Expected Answer Shape**: Table

#### Q47: Compare the skill gap for male vs female students.
- **Domain**: Cross-Domain
- **Required Tables**: silver.students, gold.skill_gap_analysis
- **Required Joins**: students -> gap analysis
- **Metric**: avg gap by gender
- **Expected SQL**:
  ```sql
  SELECT s.gender, AVG(g.gap_percentage)
  FROM placewise.silver.students s
  JOIN placewise.gold.skill_gap_analysis g ON s.student_id = g.student_id
  GROUP BY s.gender;
  ```
- **Expected Answer Shape**: Table with two rows
