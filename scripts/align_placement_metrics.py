import duckdb

con = duckdb.connect('data/placewise.duckdb')

print("Aligning department placement performance with student placement profile...")

# 1. Rebuild gold.department_placement_performance strictly using silver.placements
con.execute("""
CREATE OR REPLACE TABLE gold.department_placement_performance AS
WITH placed_per_student AS (
    SELECT student_id, MAX(ctc_lpa) AS final_placed_ctc
    FROM silver.placements
    WHERE placement_status = 'CONFIRMED'
    GROUP BY student_id
)
SELECT
    d.department_code,
    d.department_name,
    s.graduation_year,
    COUNT(DISTINCT s.student_id) AS total_students,
    COUNT(DISTINCT CASE WHEN s.placement_status IN ('ELIGIBLE','ACTIVE','PLACED') THEN s.student_id END) AS eligible_students,
    COUNT(DISTINCT p.student_id) AS placed_students,
    ROUND(COUNT(DISTINCT p.student_id) * 100.0 / NULLIF(COUNT(DISTINCT CASE WHEN s.placement_status IN ('ELIGIBLE','ACTIVE','PLACED') THEN s.student_id END), 0), 2) AS placement_rate,
    ROUND(AVG(p.final_placed_ctc), 2) AS average_ctc_lpa,
    ROUND(MEDIAN(p.final_placed_ctc), 2) AS median_ctc_lpa,
    ROUND(MAX(p.final_placed_ctc), 2) AS highest_ctc_lpa
FROM silver.departments d
JOIN silver.students s ON d.department_id = s.department_id
LEFT JOIN placed_per_student p ON s.student_id = p.student_id
GROUP BY d.department_code, d.department_name, s.graduation_year;
""")

# 2. Update semantic.genie_department_performance
con.execute("""
CREATE OR REPLACE VIEW semantic.genie_department_performance AS
WITH base AS (
    SELECT 
        d.department_code,
        d.department_name,
        d.graduation_year,
        d.total_students,
        d.eligible_students,
        d.placed_students,
        d.placement_rate,
        d.average_ctc_lpa,
        d.median_ctc_lpa,
        d.highest_ctc_lpa,
        LAG(d.placement_rate) OVER(PARTITION BY d.department_code ORDER BY d.graduation_year) AS prev_placement_rate,
        LAG(d.average_ctc_lpa) OVER(PARTITION BY d.department_code ORDER BY d.graduation_year) AS prev_average_ctc
    FROM gold.department_placement_performance d
)
SELECT 
    department_code,
    department_name,
    graduation_year,
    total_students,
    eligible_students,
    placed_students,
    placement_rate,
    average_ctc_lpa,
    median_ctc_lpa,
    highest_ctc_lpa,
    prev_placement_rate AS placement_rate_yoy,
    ROUND(placement_rate - COALESCE(prev_placement_rate, placement_rate), 2) AS placement_rate_change_points,
    prev_average_ctc AS average_ctc_yoy,
    DENSE_RANK() OVER(PARTITION BY graduation_year ORDER BY placement_rate DESC) AS rank_within_year
FROM base;
""")

print("✓ Aligned successfully.")
