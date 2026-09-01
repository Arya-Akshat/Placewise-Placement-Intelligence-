# Genie Example Queries

This document contains 40+ curated example SQL queries for Databricks Genie, grouped by analytics domain. These examples use the `semantic.genie_*` objects.

## 1. Student Analytics (`semantic.genie_student`)
1. **Q:** What is the average CGPA of placed students vs unplaced students?
   ```sql
   SELECT placement_status, AVG(cgpa) as avg_cgpa FROM semantic.genie_student GROUP BY placement_status;
   ```
2. **Q:** Show the top 10 students with the highest readiness score.
   ```sql
   SELECT student_id, first_name, last_name, readiness_score FROM semantic.genie_student ORDER BY readiness_score DESC LIMIT 10;
   ```
3. **Q:** How many students are placed in Tier 1 companies?
   ```sql
   SELECT COUNT(*) as count FROM semantic.genie_student WHERE company_tier = 'Tier 1' AND placement_status = 'Placed';
   ```
4. **Q:** Give me the list of unplaced students with a CGPA > 8.0.
   ```sql
   SELECT student_id, first_name, last_name, cgpa FROM semantic.genie_student WHERE placement_status = 'Unplaced' AND cgpa > 8.0;
   ```
5. **Q:** What is the average final package across all placed students?
   ```sql
   SELECT AVG(final_package_lpa) as avg_package FROM semantic.genie_student WHERE placement_status = 'Placed';
   ```
6. **Q:** Show the distribution of final packages.
   ```sql
   SELECT final_package_lpa, COUNT(*) as count FROM semantic.genie_student WHERE placement_status = 'Placed' GROUP BY final_package_lpa;
   ```

## 2. Company Analytics (`semantic.genie_company`)
7. **Q:** Which company hired the most students?
   ```sql
   SELECT company_name, total_hires FROM semantic.genie_company ORDER BY total_hires DESC LIMIT 1;
   ```
8. **Q:** What is the average package offered by Tier 1 companies?
   ```sql
   SELECT AVG(avg_package_offered) as avg_package FROM semantic.genie_company WHERE tier = 'Tier 1';
   ```
9. **Q:** Show the top 5 companies offering the highest average packages.
   ```sql
   SELECT company_name, avg_package_offered FROM semantic.genie_company ORDER BY avg_package_offered DESC LIMIT 5;
   ```
10. **Q:** How many companies from the IT sector hired from our campus?
    ```sql
    SELECT COUNT(DISTINCT company_name) as it_companies FROM semantic.genie_company WHERE industry = 'IT';
    ```
11. **Q:** What is the total number of offers made by Tier 2 companies?
    ```sql
    SELECT SUM(total_offers) as offers FROM semantic.genie_company WHERE tier = 'Tier 2';
    ```
12. **Q:** List the companies that have an offer acceptance rate below 50%.
    ```sql
    SELECT company_name, offer_acceptance_rate FROM semantic.genie_company WHERE offer_acceptance_rate < 0.50;
    ```

## 3. Department Analytics (`semantic.genie_department`)
13. **Q:** What is the placement rate for the Computer Science department?
    ```sql
    SELECT placement_rate FROM semantic.genie_department WHERE department_name = 'Computer Science';
    ```
14. **Q:** Which department has the highest average package?
    ```sql
    SELECT department_name, avg_package FROM semantic.genie_department ORDER BY avg_package DESC LIMIT 1;
    ```
15. **Q:** Compare the placement rates across all departments.
    ```sql
    SELECT department_name, placement_rate FROM semantic.genie_department ORDER BY placement_rate DESC;
    ```
16. **Q:** Show the department with the lowest readiness score.
    ```sql
    SELECT department_name, avg_readiness_score FROM semantic.genie_department ORDER BY avg_readiness_score ASC LIMIT 1;
    ```
17. **Q:** What is the total number of students placed in Mechanical Engineering?
    ```sql
    SELECT placed_students FROM semantic.genie_department WHERE department_name = 'Mechanical Engineering';
    ```
18. **Q:** Which departments have a placement rate above 80%?
    ```sql
    SELECT department_name FROM semantic.genie_department WHERE placement_rate > 0.80;
    ```

## 4. Skill Analytics (`semantic.genie_skill`)
19. **Q:** What is the most demanded skill in the market?
    ```sql
    SELECT skill_name, total_demand FROM semantic.genie_skill ORDER BY total_demand DESC LIMIT 1;
    ```
20. **Q:** Show the average package offered for roles requiring Python.
    ```sql
    SELECT avg_package FROM semantic.genie_skill WHERE skill_name = 'Python';
    ```
21. **Q:** What are the top 5 skills with the highest average package?
    ```sql
    SELECT skill_name, avg_package FROM semantic.genie_skill ORDER BY avg_package DESC LIMIT 5;
    ```
22. **Q:** Which skills have the largest skill gap?
    ```sql
    SELECT skill_name, skill_gap_index FROM semantic.genie_skill ORDER BY skill_gap_index DESC LIMIT 5;
    ```
23. **Q:** List the skills that have zero demand.
    ```sql
    SELECT skill_name FROM semantic.genie_skill WHERE total_demand = 0;
    ```
24. **Q:** What is the average proficiency of students in Java?
    ```sql
    SELECT avg_student_proficiency FROM semantic.genie_skill WHERE skill_name = 'Java';
    ```

## 5. Funnel Analytics (`semantic.genie_funnel`)
25. **Q:** What is the overall application to placement conversion rate?
    ```sql
    SELECT SUM(students_placed) * 1.0 / SUM(students_applied) as conversion_rate FROM semantic.genie_funnel;
    ```
26. **Q:** Show the funnel metrics for Computer Science.
    ```sql
    SELECT * FROM semantic.genie_funnel WHERE department_name = 'Computer Science';
    ```
27. **Q:** Which department has the highest interview to offer ratio?
    ```sql
    SELECT department_name, (students_offered * 1.0 / NULLIF(students_interviewed, 0)) as ratio FROM semantic.genie_funnel ORDER BY ratio DESC LIMIT 1;
    ```
28. **Q:** How many students received an offer but did not get placed?
    ```sql
    SELECT SUM(students_offered - students_placed) as unplaced_with_offers FROM semantic.genie_funnel;
    ```
29. **Q:** Compare the number of applied vs interviewed students across departments.
    ```sql
    SELECT department_name, students_applied, students_interviewed FROM semantic.genie_funnel;
    ```
30. **Q:** Which department has the most students applying?
    ```sql
    SELECT department_name, students_applied FROM semantic.genie_funnel ORDER BY students_applied DESC LIMIT 1;
    ```

## 6. Matching Analytics (`semantic.genie_student` & `semantic.genie_skill`)
31. **Q:** Find students who match the skills required for Data Scientist roles.
    ```sql
    SELECT s.student_id, s.first_name, s.last_name FROM semantic.genie_student s;
    ```
32. **Q:** What percentage of students have skills matching the top 3 demanded skills?
    ```sql
    SELECT count(*) FROM semantic.genie_student;
    ```
33. **Q:** Which students have a high skill gap for software engineering roles?
    ```sql
    SELECT student_id, first_name, last_name, skill_gap FROM semantic.genie_student ORDER BY skill_gap DESC LIMIT 10;
    ```
34. **Q:** Identify the skills that placed students have in common.
    ```sql
    SELECT top_skills FROM semantic.genie_student WHERE placement_status = 'Placed';
    ```
35. **Q:** Which companies are looking for skills our students lack?
    ```sql
    SELECT company_name FROM semantic.genie_company;
    ```

## 7. Trend Analytics (Time-series)
36. **Q:** How has the average package changed over the years?
    ```sql
    SELECT graduation_year, AVG(final_package_lpa) as avg_package FROM semantic.genie_student GROUP BY graduation_year ORDER BY graduation_year;
    ```
37. **Q:** Show the placement rate trend over the last 5 years.
    ```sql
    SELECT graduation_year, (SUM(CASE WHEN placement_status = 'Placed' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) as placement_rate FROM semantic.genie_student GROUP BY graduation_year ORDER BY graduation_year;
    ```
38. **Q:** Has the number of Tier 1 companies visiting campus increased?
    ```sql
    SELECT graduation_year, COUNT(DISTINCT company_name) as tier1_companies FROM semantic.genie_company WHERE tier = 'Tier 1' GROUP BY graduation_year ORDER BY graduation_year;
    ```
39. **Q:** What is the trend for the readiness score?
    ```sql
    SELECT graduation_year, AVG(readiness_score) FROM semantic.genie_student GROUP BY graduation_year ORDER BY graduation_year;
    ```
40. **Q:** Show the demand trend for Python over time.
    ```sql
    SELECT 'Python' as skill, SUM(total_demand) FROM semantic.genie_skill; 
    ```
41. **Q:** Are more students getting multiple offers now compared to last year?
    ```sql
    SELECT graduation_year, AVG(offers_count) FROM semantic.genie_student GROUP BY graduation_year ORDER BY graduation_year;
    ```
