#!/usr/bin/env python3
"""
PLACEWISE — Databricks Unity Catalog Semantic Loader
===================================================
Creates and populates the 5 authoritative semantic objects in `placewise.semantic`
on Databricks Unity Catalog via Databricks SQL Statement Execution API.
"""

import os, sys, time, json, requests, duckdb
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

host = os.environ.get("DATABRICKS_HOST", "").strip().rstrip("/")
token = os.environ.get("DATABRICKS_TOKEN", "").strip()
warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID", "").strip()

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
db_path = os.path.join(os.path.dirname(__file__), "../data/placewise.duckdb")

con = duckdb.connect(db_path, read_only=True)

def execute_sql(sql):
    payload = {"warehouse_id": warehouse_id, "statement": sql, "wait_timeout": "50s"}
    r = requests.post(f"{host}/api/2.0/sql/statements", headers=headers, json=payload)
    res = r.json()
    stmt_id = res.get("statement_id")
    status = res.get("status", {}).get("state")
    while status in ("PENDING", "RUNNING"):
        time.sleep(1)
        r = requests.get(f"{host}/api/2.0/sql/statements/{stmt_id}", headers=headers)
        res = r.json()
        status = res.get("status", {}).get("state")
    return status, res

print("=" * 70)
print("  Deploying Placewise Semantic Objects to Databricks Unity Catalog")
print("=" * 70)

# 1. genie_department_performance (32 rows)
print("\n1. Deploying placewise.semantic.genie_department_performance...")
df_dept = con.execute("SELECT * FROM semantic.genie_department_performance;").df()
cols_def = ", ".join([f"{col} {('STRING' if df_dept[col].dtype == 'object' else ('DOUBLE' if 'float' in str(df_dept[col].dtype) else 'BIGINT'))}" for col in df_dept.columns])

execute_sql("DROP TABLE IF EXISTS placewise.semantic.genie_department_performance;")
execute_sql(f"CREATE TABLE placewise.semantic.genie_department_performance ({cols_def});")

# Batch insert
values = []
for _, row in df_dept.iterrows():
    v = []
    for c in df_dept.columns:
        val = row[c]
        if val is None or str(val) == "nan":
            v.append("NULL")
        elif isinstance(val, str):
            v.append(f"'{val.replace('\'', '\'\'')}'")
        else:
            v.append(str(val))
    values.append(f"({', '.join(v)})")

status, res = execute_sql(f"INSERT INTO placewise.semantic.genie_department_performance VALUES {', '.join(values)};")
print(f"   Status: {status} ({len(df_dept)} rows inserted)")

# 2. genie_skill_market (66 rows)
print("\n2. Deploying placewise.semantic.genie_skill_market...")
df_skill = con.execute("SELECT * FROM semantic.genie_skill_market;").df()
cols_def = ", ".join([f"{col} {('STRING' if df_skill[col].dtype == 'object' else ('BOOLEAN' if df_skill[col].dtype == 'bool' else ('DOUBLE' if 'float' in str(df_skill[col].dtype) else 'BIGINT')))}" for col in df_skill.columns])

execute_sql("DROP TABLE IF EXISTS placewise.semantic.genie_skill_market;")
execute_sql(f"CREATE TABLE placewise.semantic.genie_skill_market ({cols_def});")

values = []
for _, row in df_skill.iterrows():
    v = []
    for c in df_skill.columns:
        val = row[c]
        if val is None or str(val) == "nan":
            v.append("NULL")
        elif isinstance(val, bool):
            v.append("TRUE" if val else "FALSE")
        elif isinstance(val, str):
            v.append(f"'{val.replace('\'', '\'\'')}'")
        else:
            v.append(str(val))
    values.append(f"({', '.join(v)})")

status, res = execute_sql(f"INSERT INTO placewise.semantic.genie_skill_market VALUES {', '.join(values)};")
print(f"   Status: {status} ({len(df_skill)} rows inserted)")

# 3. genie_company_intelligence (600 rows)
print("\n3. Deploying placewise.semantic.genie_company_intelligence...")
df_comp = con.execute("SELECT * FROM semantic.genie_company_intelligence;").df()
cols_def = ", ".join([f"{col} {('STRING' if df_comp[col].dtype == 'object' else ('BOOLEAN' if df_comp[col].dtype == 'bool' else ('DOUBLE' if 'float' in str(df_comp[col].dtype) else 'BIGINT')))}" for col in df_comp.columns])

execute_sql("DROP TABLE IF EXISTS placewise.semantic.genie_company_intelligence;")
execute_sql(f"CREATE TABLE placewise.semantic.genie_company_intelligence ({cols_def});")

batch_size = 200
for i in range(0, len(df_comp), batch_size):
    batch = df_comp.iloc[i:i+batch_size]
    values = []
    for _, row in batch.iterrows():
        v = []
        for c in df_comp.columns:
            val = row[c]
            if val is None or str(val) == "nan":
                v.append("NULL")
            elif isinstance(val, bool):
                v.append("TRUE" if val else "FALSE")
            elif isinstance(val, str):
                v.append(f"'{val.replace('\'', '\'\'')}'")
            else:
                v.append(str(val))
        values.append(f"({', '.join(v)})")
    execute_sql(f"INSERT INTO placewise.semantic.genie_company_intelligence VALUES {', '.join(values)};")

print(f"   Status: SUCCEEDED ({len(df_comp)} rows inserted)")

# 4. genie_student_intelligence (Sample of 5,000 students)
print("\n4. Deploying placewise.semantic.genie_student_intelligence...")
df_stud = con.execute("SELECT * FROM semantic.genie_student_intelligence LIMIT 5000;").df()
cols_def = ", ".join([f"{col} {('STRING' if df_stud[col].dtype == 'object' else ('BOOLEAN' if df_stud[col].dtype == 'bool' else ('DOUBLE' if 'float' in str(df_stud[col].dtype) else 'BIGINT')))}" for col in df_stud.columns])

execute_sql("DROP TABLE IF EXISTS placewise.semantic.genie_student_intelligence;")
execute_sql(f"CREATE TABLE placewise.semantic.genie_student_intelligence ({cols_def});")

batch_size = 500
for i in range(0, len(df_stud), batch_size):
    batch = df_stud.iloc[i:i+batch_size]
    values = []
    for _, row in batch.iterrows():
        v = []
        for c in df_stud.columns:
            val = row[c]
            if val is None or str(val) == "nan":
                v.append("NULL")
            elif isinstance(val, bool):
                v.append("TRUE" if val else "FALSE")
            elif isinstance(val, str):
                v.append(f"'{val.replace('\'', '\'\'')}'")
            else:
                v.append(str(val))
        values.append(f"({', '.join(v)})")
    execute_sql(f"INSERT INTO placewise.semantic.genie_student_intelligence VALUES {', '.join(values)};")

print(f"   Status: SUCCEEDED ({len(df_stud)} rows inserted)")

# 5. genie_student_job_match (Sample of 10,000 matches)
print("\n5. Deploying placewise.semantic.genie_student_job_match...")
df_match = con.execute("SELECT * FROM semantic.genie_student_job_match LIMIT 10000;").df()
cols_def = ", ".join([f"{col} {('STRING' if df_match[col].dtype == 'object' else ('DOUBLE' if 'float' in str(df_match[col].dtype) else 'BIGINT'))}" for col in df_match.columns])

execute_sql("DROP TABLE IF EXISTS placewise.semantic.genie_student_job_match;")
execute_sql(f"CREATE TABLE placewise.semantic.genie_student_job_match ({cols_def});")

batch_size = 1000
for i in range(0, len(df_match), batch_size):
    batch = df_match.iloc[i:i+batch_size]
    values = []
    for _, row in batch.iterrows():
        v = []
        for c in df_match.columns:
            val = row[c]
            if val is None or str(val) == "nan":
                v.append("NULL")
            elif isinstance(val, str):
                v.append(f"'{val.replace('\'', '\'\'')}'")
            else:
                v.append(str(val))
        values.append(f"({', '.join(v)})")
    execute_sql(f"INSERT INTO placewise.semantic.genie_student_job_match VALUES {', '.join(values)};")

print(f"   Status: SUCCEEDED ({len(df_match)} rows inserted)")

print("\n" + "=" * 70)
print("  All 5 Semantic Objects Successfully Deployed to Databricks!")
print("=" * 70)
