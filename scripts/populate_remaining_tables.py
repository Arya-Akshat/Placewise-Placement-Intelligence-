#!/usr/bin/env python3
"""
Populates genie_company_intelligence, genie_student_intelligence, and genie_student_job_match
in Databricks Unity Catalog placewise.semantic schema.
"""

import os, requests, time, duckdb
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

host = os.environ.get("DATABRICKS_HOST", "").strip().rstrip("/")
token = os.environ.get("DATABRICKS_TOKEN", "").strip()
warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID", "").strip()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
con = duckdb.connect(os.path.join(os.path.dirname(__file__), "../data/placewise.duckdb"), read_only=True)

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
    if status != "SUCCEEDED":
        print("SQL Error:", res.get("status", {}).get("error"))
    return status, res

# 1. genie_company_intelligence (600 rows)
print("\n1. Populating placewise.semantic.genie_company_intelligence...")
df_comp = con.execute("SELECT * FROM semantic.genie_company_intelligence;").df()
execute_sql("DROP TABLE IF EXISTS placewise.semantic.genie_company_intelligence;")
cols = list(df_comp.columns)
cols_types = []
for c in cols:
    t = df_comp[c].dtype
    if "bool" in str(t):
        cols_types.append(f"{c} BOOLEAN")
    elif "float" in str(t):
        cols_types.append(f"{c} DOUBLE")
    elif "int" in str(t):
        cols_types.append(f"{c} BIGINT")
    else:
        cols_types.append(f"{c} STRING")

execute_sql(f"CREATE TABLE placewise.semantic.genie_company_intelligence ({', '.join(cols_types)});")

batch_size = 100
for i in range(0, len(df_comp), batch_size):
    batch = df_comp.iloc[i:i+batch_size]
    values = []
    for _, row in batch.iterrows():
        v = []
        for c in cols:
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

print("   ✓ genie_company_intelligence populated.")

# 2. genie_student_intelligence (1000 sample rows)
print("\n2. Populating placewise.semantic.genie_student_intelligence...")
df_stud = con.execute("SELECT * FROM semantic.genie_student_intelligence LIMIT 1000;").df()
execute_sql("DROP TABLE IF EXISTS placewise.semantic.genie_student_intelligence;")
cols_s = list(df_stud.columns)
cols_types_s = []
for c in cols_s:
    t = df_stud[c].dtype
    if "bool" in str(t):
        cols_types_s.append(f"{c} BOOLEAN")
    elif "float" in str(t):
        cols_types_s.append(f"{c} DOUBLE")
    elif "int" in str(t):
        cols_types_s.append(f"{c} BIGINT")
    else:
        cols_types_s.append(f"{c} STRING")

execute_sql(f"CREATE TABLE placewise.semantic.genie_student_intelligence ({', '.join(cols_types_s)});")

batch_size = 100
for i in range(0, len(df_stud), batch_size):
    batch = df_stud.iloc[i:i+batch_size]
    values = []
    for _, row in batch.iterrows():
        v = []
        for c in cols_s:
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

print("   ✓ genie_student_intelligence populated.")

# 3. genie_student_job_match (1000 sample rows)
print("\n3. Populating placewise.semantic.genie_student_job_match...")
df_match = con.execute("SELECT * FROM semantic.genie_student_job_match LIMIT 1000;").df()
execute_sql("DROP TABLE IF EXISTS placewise.semantic.genie_student_job_match;")
cols_m = list(df_match.columns)
cols_types_m = []
for c in cols_m:
    t = df_match[c].dtype
    if "bool" in str(t):
        cols_types_m.append(f"{c} BOOLEAN")
    elif "float" in str(t):
        cols_types_m.append(f"{c} DOUBLE")
    elif "int" in str(t):
        cols_types_m.append(f"{c} BIGINT")
    else:
        cols_types_m.append(f"{c} STRING")

execute_sql(f"CREATE TABLE placewise.semantic.genie_student_job_match ({', '.join(cols_types_m)});")

batch_size = 200
for i in range(0, len(df_match), batch_size):
    batch = df_match.iloc[i:i+batch_size]
    values = []
    for _, row in batch.iterrows():
        v = []
        for c in cols_m:
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
    execute_sql(f"INSERT INTO placewise.semantic.genie_student_job_match VALUES {', '.join(values)};")

print("   ✓ genie_student_job_match populated.")
