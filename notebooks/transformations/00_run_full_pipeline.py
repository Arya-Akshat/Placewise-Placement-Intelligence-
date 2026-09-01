# Databricks notebook: Run Full Placewise Pipeline
# Run this to execute all Bronze→Silver→Gold transformations in order.
# Idempotent: safe to re-run.

import os
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

CATALOG = spark.conf.get("placewise.catalog", "placewise")
print(f"Running pipeline for catalog: {CATALOG}")

def run_sql_file(path: str):
    with open(path) as f:
        sql = f.read()
    # Handle multi-statement files separated by semicolons
    stmts = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
    for stmt in stmts:
        spark.sql(stmt)
    print(f"  ✓ {path}")

print("\n=== Phase 1: Schema Setup ===")
run_sql_file("/Workspace/Repos/placewise/databricks/schemas/create_schemas.sql")

print("\n=== Phase 2: Silver DDL ===")
import glob
for f in sorted(glob.glob("/Workspace/Repos/placewise/sql/ddl/silver/*.sql")):
    run_sql_file(f)

print("\n=== Phase 3: Gold DDL ===")
for f in sorted(glob.glob("/Workspace/Repos/placewise/sql/ddl/gold/*.sql")):
    run_sql_file(f)

print("\n=== Phase 4: Semantic Views ===")
for f in sorted(glob.glob("/Workspace/Repos/placewise/sql/ddl/semantic/*.sql")):
    run_sql_file(f)

print("\n=== Phase 5: Bronze→Silver Transformations ===")
for f in sorted(glob.glob("/Workspace/Repos/placewise/sql/transformations/bronze_to_silver_*.sql")):
    run_sql_file(f)

print("\n=== Phase 6: Silver→Gold Transformations ===")
# Order matters — dims before facts before derived tables
TRANSFORM_ORDER = [
    "silver_to_gold_dim_date.sql",
    "silver_to_gold_student_placement_profile.sql",
    "silver_to_gold_student_job_skill_match.sql",
    "silver_to_gold_company_hiring_profile.sql",
    "silver_to_gold_department_placement_performance.sql",
    "silver_to_gold_skill_demand_profile.sql",
]
base = "/Workspace/Repos/placewise/sql/transformations/"
for name in TRANSFORM_ORDER:
    run_sql_file(base + name)

print("\n✅ Full pipeline complete.")
