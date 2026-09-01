CREATE OR REPLACE TABLE placewise.gold.dim_date AS
WITH RECURSIVE dates AS (
    SELECT CAST('2010-01-01' AS DATE) AS date_val
    UNION ALL
    SELECT date_add(date_val, 1) FROM dates WHERE date_val < CAST('2035-12-31' AS DATE)
)
SELECT 
    date_val AS date,
    YEAR(date_val) AS year,
    MONTH(date_val) AS month,
    DAY(date_val) AS day,
    CONCAT('AY', YEAR(date_add(date_val, -6)), '-', SUBSTRING(CAST(YEAR(date_add(date_val, 6)) AS STRING), 3, 2)) AS academic_year,
    CONCAT('PS', YEAR(date_add(date_val, -7))) AS placement_season,
    CASE WHEN MONTH(date_val) IN (8,9,10,11,12) THEN 1 ELSE 2 END AS semester
FROM dates;\n