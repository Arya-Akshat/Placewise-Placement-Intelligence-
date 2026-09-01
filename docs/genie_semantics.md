# Genie Semantics

## Setup Guide
To enable natural language querying in Databricks Genie:
1. Create a Genie Space based on the `placewise_semantic` catalog/schema.
2. Ensure underlying tables (`semantic_student_placement`, `semantic_company_hiring`) have primary keys and foreign keys defined in Unity Catalog.
3. Import the glossary and instructions below into the Genie Space instructions block.

## Business Terminology Glossary
- **Placed**: A student who has received and accepted at least one job offer (`placement_status = 'Placed'`).
- **Offer vs Placement**: An 'offer' is extended by a company; a 'placement' is an offer accepted by a student. Our primary metrics track 'placements'.
- **Package**: The annual compensation. Synonyms: CTC, salary, compensation, LPA (Lakhs Per Annum).
- **Placement Rate**: Synonyms: selection rate, hiring percentage.
- **Interview Conversion**: The rate at which an interview round results in a 'Pass'.
- **Skill Gap**: The difference between skills required by a job and skills possessed by a student.
- **Readiness Score**: A 0-100 composite index predicting placement success based on academics, skills, and mock interviews.

## Recommended Genie Spaces Configuration
- **Default Timeframe**: If no year is specified, default to `graduation_year = YEAR(CURRENT_DATE)`.
- **Currency Context**: All monetary values (package, salary) are in LPA.

## Tables to Expose
- `semantic_student_placement_fact`: One row per student per placement.
- `semantic_company_hiring_fact`: One row per company per year.
- `semantic_department_dim`: Department details.

## Dimensions & Measures
- **Dimensions**: `department_name`, `company_tier`, `industry`, `gender`, `role_title`, `graduation_year`.
- **Measures**: `avg_package_lpa` (Average), `total_placements` (Sum), `placement_rate` (Custom Expression).

## Example Questions & SQL Patterns

### Student Domain
**Q:** "What is the average CGPA of placed students vs unplaced students?"
**Expected SQL:**
```sql
SELECT placement_status, AVG(cgpa)
FROM semantic_student_placement
GROUP BY placement_status
```

### Company Domain
**Q:** "Which Tier 1 company offered the highest package?"
**Expected SQL:**
```sql
SELECT company_name, MAX(final_package_lpa)
FROM semantic_company_hiring
WHERE tier = 'Tier 1'
GROUP BY company_name
ORDER BY 2 DESC LIMIT 1
```

### Department Domain
**Q:** "What is the placement rate for Computer Science?"
**Expected SQL:**
```sql
SELECT (placed_students * 100.0 / total_students) AS placement_rate
FROM semantic_department_dim
WHERE department_name = 'Computer Science'
```

## Genie Instructions Text
*(Copy-paste into Genie)*
> You are analyzing campus placement data for Placewise.
> - Always assume 'salary', 'package', 'CTC' refers to `final_package_lpa`.
> - If asked for 'placement rate', calculate `(placed_students / total_students)`.
> - 'Current year' means the most recent `graduation_year` in the dataset.
> - Only use tables in the `placewise_semantic` schema.
