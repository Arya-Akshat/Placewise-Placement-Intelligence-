# Databricks notebook: Ingest CSV files into Bronze layer
# Usage: Mount your source data to /mnt/placewise-raw/ and run this notebook.
# Reads CSV/Excel files and writes raw records to Bronze Delta tables.

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name, lit

spark = SparkSession.builder.getOrCreate()

SOURCE_PATH  = spark.conf.get("placewise.source_path",  "/mnt/placewise-raw")
CATALOG      = spark.conf.get("placewise.catalog",      "placewise")
BRONZE       = f"{CATALOG}.bronze"

TABLE_MAP = {
    "students":                   f"{BRONZE}.students_raw",
    "companies":                  f"{BRONZE}.companies_raw",
    "departments":                f"{BRONZE}.departments_raw",
    "academic_programs":          f"{BRONZE}.academic_programs_raw",
    "cohorts":                    f"{BRONZE}.cohorts_raw",
    "job_postings":               f"{BRONZE}.job_postings_raw",
    "job_roles":                  f"{BRONZE}.job_roles_raw",
    "applications":               f"{BRONZE}.applications_raw",
    "interviews":                 f"{BRONZE}.interviews_raw",
    "offers":                     f"{BRONZE}.offers_raw",
    "placements":                 f"{BRONZE}.placements_raw",
    "skills":                     f"{BRONZE}.skills_raw",
    "student_skills":             f"{BRONZE}.student_skills_raw",
    "job_required_skills":        f"{BRONZE}.job_required_skills_raw",
    "projects":                   f"{BRONZE}.projects_raw",
    "student_projects":           f"{BRONZE}.student_projects_raw",
    "internships":                f"{BRONZE}.internships_raw",
}

def ingest_csv(name, target_table):
    path = f"{SOURCE_PATH}/{name}.csv"
    try:
        df = (spark.read
              .option("header", True)
              .option("inferSchema", False)  # keep everything as STRING in bronze
              .option("multiLine", True)
              .option("escape", '"')
              .csv(path))
        df = (df
              .withColumn("_ingested_at", current_timestamp())
              .withColumn("_source_file", input_file_name()))
        (df.write
           .format("delta")
           .mode("append")
           .option("mergeSchema", "true")
           .saveAsTable(target_table))
        print(f"  ✓ {name} → {target_table} ({df.count()} rows)")
    except Exception as e:
        print(f"  ✗ {name}: {e}")

print("=== Ingesting source files to Bronze ===")
for name, table in TABLE_MAP.items():
    ingest_csv(name, table)
print("Ingestion complete.")
