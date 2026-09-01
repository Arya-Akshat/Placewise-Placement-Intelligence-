# Question Traceability

| Question | Required Tables | Required Joins | Required Metric | Semantic Object | Example SQL |
|---|---|---|---|---|---|
| **Student Domain** | | | | | |
| What is the average CGPA of unplaced students? | `semantic_student_placement` | None | Average CGPA | `avg_cgpa` | `SELECT AVG(cgpa) FROM semantic_student_placement WHERE placement_status = 'Unplaced'` |
| Show me students with CGPA > 9 who are unplaced. | `semantic_student_placement` | None | N/A | `student_name` | `SELECT student_name FROM semantic_student_placement WHERE cgpa > 9 AND placement_status = 'Unplaced'` |
| **Company Domain** | | | | | |
| Which company hired the most students? | `semantic_company_hiring` | None | Company Hiring Count | `total_hired` | `SELECT company_name, SUM(total_hired) FROM semantic_company_hiring GROUP BY company_name ORDER BY 2 DESC LIMIT 1` |
| What is the average package offered by Tier 1 companies? | `semantic_company_hiring` | None | Average Package | `avg_package_lpa` | `SELECT AVG(avg_package_lpa) FROM semantic_company_hiring WHERE tier = 'Tier 1'` |
| **Department Domain** | | | | | |
| Which department has the highest placement rate? | `semantic_department_dim` | None | Placement Rate | `placement_rate` | `SELECT department_name, (placed/total) as pr FROM semantic_department_dim ORDER BY pr DESC LIMIT 1` |
| **Skill Domain** | | | | | |
| What are the top 3 most demanded skills? | `semantic_job_skills` | None | Skill Demand | `job_count` | `SELECT skill_name, COUNT(job_id) FROM semantic_job_skills GROUP BY skill_name ORDER BY 2 DESC LIMIT 3` |
| **Funnel Domain** | | | | | |
| What is the application conversion rate for TechNova? | `semantic_company_funnel` | None | App Conversion Rate | `app_conversion_pct` | `SELECT app_conversion_pct FROM semantic_company_funnel WHERE company_name = 'TechNova'` |
| **Time-Series Domain** | | | | | |
| How has the average package changed over the last 3 years? | `semantic_placement_trends` | None | Average Package | `avg_package_lpa`, `year` | `SELECT year, AVG(avg_package_lpa) FROM semantic_placement_trends GROUP BY year ORDER BY year` |
| **Cross-Domain** | | | | | |
| Do students with higher interview scores get higher packages? | `semantic_student_placement` | None | Avg Score, Avg Pkg | `interview_score`, `package` | `SELECT CORR(interview_score, final_package_lpa) FROM semantic_student_placement` |

*(Note: Table shows a representative sample covering all requested domains. In full deployment, this expands to 40+ specific variations.)*
