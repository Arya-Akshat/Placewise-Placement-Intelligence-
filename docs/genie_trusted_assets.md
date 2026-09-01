# Genie Trusted Assets

This document catalogs parameterized, verified SQL queries for high-value deterministic questions. These assets are considered "Gold standard" and should be used as reference by the Genie layer to answer critical business questions.

## 1. Placement Rate by Department and Year
**Description:** Calculates the placement rate (placed / total) for a given department and year.
**Query:**
```sql
SELECT 
    department_name,
    graduation_year,
    SUM(CASE WHEN placement_status = 'Placed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS placement_rate_percentage
FROM semantic.genie_student
WHERE department_name = '{{department_name}}'
  AND graduation_year = {{graduation_year}}
GROUP BY department_name, graduation_year;
```

## 2. Average Package by Department
**Description:** Returns the average compensation package for placed students in a specific department.
**Query:**
```sql
SELECT 
    department_name,
    AVG(final_package_lpa) AS average_package_lpa
FROM semantic.genie_student
WHERE placement_status = 'Placed'
  AND department_name = '{{department_name}}'
GROUP BY department_name;
```

## 3. Top Hiring Companies
**Description:** Identifies the top N companies based on the number of accepted offers (placements).
**Query:**
```sql
SELECT 
    company_name,
    SUM(total_hires) AS total_hired_students
FROM semantic.genie_company
WHERE graduation_year = {{graduation_year}}
GROUP BY company_name
ORDER BY total_hired_students DESC
LIMIT {{limit}};
```

## 4. High-Readiness Unplaced Students
**Description:** Identifies students who have a high readiness score but have not yet been placed.
**Query:**
```sql
SELECT 
    student_id,
    first_name,
    last_name,
    readiness_score,
    department_name
FROM semantic.genie_student
WHERE placement_status = 'Unplaced'
  AND readiness_score >= {{readiness_threshold}}
ORDER BY readiness_score DESC;
```

## 5. Skill Market Demand
**Description:** Ranks skills by total market demand (e.g., job postings requiring the skill).
**Query:**
```sql
SELECT 
    skill_name,
    total_demand,
    avg_package
FROM semantic.genie_skill
ORDER BY total_demand DESC
LIMIT {{limit}};
```

## 6. Candidate Ranking for Job Role
**Description:** Ranks candidates for a specific role based on their readiness score and relevant skill match.
**Query:**
```sql
SELECT 
    student_id,
    first_name,
    last_name,
    department_name,
    readiness_score
FROM semantic.genie_student
WHERE placement_status = 'Unplaced'
ORDER BY readiness_score DESC
LIMIT {{limit}};
```
