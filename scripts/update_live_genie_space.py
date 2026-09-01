#!/usr/bin/env python3
"""
PLACEWISE — Databricks Genie Space Synchronizer
==============================================
Attaches the 5 placewise.semantic tables and injects global instructions into the live Genie space.
"""

import os, requests, json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../backend/.env"))

host = os.environ.get("DATABRICKS_HOST", "").strip().rstrip("/")
token = os.environ.get("DATABRICKS_TOKEN", "").strip()
space_id = os.environ.get("DATABRICKS_GENIE_SPACE_ID", "").strip()
warehouse_id = os.environ.get("DATABRICKS_WAREHOUSE_ID", "").strip()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Read global instructions
instructions_path = os.path.join(os.path.dirname(__file__), "../genie/instructions/global_instructions.md")
with open(instructions_path, "r", encoding="utf-8") as f:
    instructions_text = f.read()

# Build serialized space structure
tables_list = [
    {
        "table_name": "placewise.semantic.genie_department_performance",
        "description": "Department-level placement KPIs, year-over-year performance, and batch trends.",
        "enable_format_assistance": True
    },
    {
        "table_name": "placewise.semantic.genie_company_intelligence",
        "description": "Company-level hiring performance, recruitment volumes, compensation (CTC in LPA), and conversion rates.",
        "enable_format_assistance": True
    },
    {
        "table_name": "placewise.semantic.genie_skill_market",
        "description": "Recruiter skill demand, student supply, and supply-demand gaps.",
        "enable_format_assistance": True
    },
    {
        "table_name": "placewise.semantic.genie_student_intelligence",
        "description": "Student placement profiles, readiness scores, capability bands, and offer status.",
        "enable_format_assistance": True
    },
    {
        "table_name": "placewise.semantic.genie_student_job_match",
        "description": "Student-job matching matrix, skill gaps, mandatory requirement gates, and fit rankings.",
        "enable_format_assistance": True
    }
]

serialized_space_obj = {
    "version": 2,
    "space": {
        "instructions": instructions_text,
        "tables": tables_list
    }
}

payload = {
    "title": "Placewise Placement Intelligence",
    "description": "AI-powered campus placement intelligence platform querying governed semantic tables: placewise.semantic.genie_department_performance, placewise.semantic.genie_company_intelligence, placewise.semantic.genie_skill_market, placewise.semantic.genie_student_intelligence, and placewise.semantic.genie_student_job_match.",
    "warehouse_id": warehouse_id,
    "serialized_space": json.dumps(serialized_space_obj)
}

print(f"Updating Databricks Genie Space '{space_id}' with 5 placewise.semantic tables...")
r = requests.patch(f"{host}/api/2.0/genie/spaces/{space_id}", headers=headers, json=payload)
print("Patch Status:", r.status_code)
if r.ok:
    print("✓ Successfully configured Databricks Genie Space with all 5 Placewise semantic objects!")
else:
    print("Error updating space:", r.text)
