import duckdb

con = duckdb.connect('data/placewise.duckdb')

con.execute("CREATE SCHEMA IF NOT EXISTS semantic;")

con.execute("""
CREATE OR REPLACE VIEW semantic.genie_student AS
SELECT * FROM semantic.student_placement_metrics;
""")

con.execute("""
CREATE OR REPLACE VIEW semantic.genie_company AS
SELECT * FROM semantic.company_hiring_metrics;
""")

con.execute("""
CREATE OR REPLACE VIEW semantic.genie_department AS
SELECT * FROM semantic.department_placement_metrics;
""")

con.execute("""
CREATE OR REPLACE VIEW semantic.genie_skill AS
SELECT * FROM semantic.skill_demand_metrics;
""")

con.execute("""
CREATE OR REPLACE VIEW semantic.genie_funnel AS
SELECT 
    department_name,
    COUNT(*) as total_students,
    SUM(CASE WHEN applications_count > 0 THEN 1 ELSE 0 END) as students_applied,
    SUM(CASE WHEN interviews_count > 0 THEN 1 ELSE 0 END) as students_interviewed,
    SUM(CASE WHEN offers_count > 0 THEN 1 ELSE 0 END) as students_offered,
    SUM(CASE WHEN placement_status = 'Placed' THEN 1 ELSE 0 END) as students_placed
FROM semantic.student_placement_metrics
GROUP BY department_name;
""")

print("Views created successfully!")
