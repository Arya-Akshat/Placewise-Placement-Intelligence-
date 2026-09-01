#!/usr/bin/env python3
"""
Robust loader for Databricks Unity Catalog placewise.semantic tables.
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
        print("SQL Error:", res.get("status", {}).get("error", {}).get("message"))
    return status, res

def format_val(val, dtype_str):
    if val is None or str(val) == "nan" or str(val) == "NaT" or str(val) == "<NA>":
        return "NULL"
    if "bool" in dtype_str:
        return "TRUE" if val else "FALSE"
    if "float" in dtype_str or "int" in dtype_str:
        try:
            float(val)
            return str(val)
        except Exception:
            return "NULL"
    # String / Timestamp / Other
    s = str(val).replace("'", "''")
    return f"'{s}'"

def load_table(table_name, limit=None):
    print(f"\nPopulating placewise.semantic.{table_name}...")
    query = f"SELECT * FROM semantic.{table_name}"
    if limit:
        query += f" LIMIT {limit}"
    df = con.execute(query).df()
    
    cols = list(df.columns)
    cols_types = []
    for c in cols:
        t = str(df[c].dtype)
        if "bool" in t:
            cols_types.append(f"{c} BOOLEAN")
        elif "float" in t:
            cols_types.append(f"{c} DOUBLE")
        elif "int" in t:
            cols_types.append(f"{c} BIGINT")
        else:
            cols_types.append(f"{c} STRING")

    execute_sql(f"DROP TABLE IF EXISTS placewise.semantic.{table_name};")
    execute_sql(f"CREATE TABLE placewise.semantic.{table_name} ({', '.join(cols_types)});")

    batch_size = 100
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        values = []
        for _, row in batch.iterrows():
            v = [format_val(row[c], str(df[c].dtype)) for c in cols]
            values.append(f"({', '.join(v)})")
        execute_sql(f"INSERT INTO placewise.semantic.{table_name} VALUES {', '.join(values)};")

    print(f"✓ {table_name} populated ({len(df)} rows).")

load_table("genie_company_intelligence")
load_table("genie_student_intelligence", limit=1000)
load_table("genie_student_job_match", limit=1000)
