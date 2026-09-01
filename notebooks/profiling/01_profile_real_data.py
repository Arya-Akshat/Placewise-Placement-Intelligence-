# Databricks notebook: Profile real placement data before ingestion
# Run this BEFORE any Silver transformations when real data arrives.
# Outputs a data profile report to help build source → canonical mapping.

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, countDistinct, when, isnan, isnull, min, max, mean, stddev, approx_percentile
import pandas as pd

spark = SparkSession.builder.getOrCreate()

SOURCE_TABLE = dbutils.widgets.get("source_table")  # e.g. "placewise.bronze.students_raw"

df = spark.table(SOURCE_TABLE)
total = df.count()

print(f"\nProfiling: {SOURCE_TABLE}  ({total} rows, {len(df.columns)} columns)\n")

results = []
for col_name in df.columns:
    c = df.select(col_name).alias("v")
    null_count = df.filter(col(col_name).isNull() | (col(col_name).cast("string") == "")).count()
    distinct   = df.select(countDistinct(col_name)).collect()[0][0]
    sample     = [r[0] for r in df.select(col_name).dropna().limit(5).collect()]
    results.append({
        "column":       col_name,
        "null_count":   null_count,
        "null_rate":    round(null_count / total * 100, 2) if total > 0 else None,
        "cardinality":  distinct,
        "sample_values": str(sample)
    })

profile_df = pd.DataFrame(results)
display(spark.createDataFrame(profile_df))

# Save profile to sandbox
spark.createDataFrame(profile_df).write.format("delta").mode("overwrite") \
    .saveAsTable(f"placewise.sandbox.profile_{SOURCE_TABLE.replace('.','_')}")
print(f"\nProfile saved to placewise.sandbox.profile_{SOURCE_TABLE.replace('.','_')}")
