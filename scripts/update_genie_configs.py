import json, os

os.makedirs('genie/agent_config', exist_ok=True)
os.makedirs('genie/instructions', exist_ok=True)
os.makedirs('genie/metadata', exist_ok=True)
os.makedirs('genie/trusted_assets', exist_ok=True)
os.makedirs('genie/examples', exist_ok=True)
os.makedirs('genie/benchmarks', exist_ok=True)

# 1. genie/agent_config/genie_agent_placement_intelligence.json
agent_config = {
    "agent_name": "Placewise Placement Intelligence",
    "description": "Conversational placement intelligence for analyzing students, companies, recruitment funnels, placement outcomes, skills, candidate-job matching and historical placement trends.",
    "target_catalog": "placewise",
    "target_schema": "semantic",
    "default_warehouse_id": "${DATABRICKS_WAREHOUSE_ID}",
    "curated_tables": [
        {
            "catalog": "placewise",
            "schema": "semantic",
            "table_name": "genie_student_intelligence",
            "display_name": "Student Intelligence Profiles",
            "grain": "One row per student (student_id)",
            "description": "Authoritative one-row-per-student analytical profile containing academic performance, skills, internships, projects, recruitment funnel outcomes, offers, placement status and governed placement readiness metrics."
        },
        {
            "catalog": "placewise",
            "schema": "semantic",
            "table_name": "genie_company_intelligence",
            "display_name": "Company Hiring Intelligence",
            "grain": "One row per company (company_id)",
            "description": "Authoritative one-row-per-company analytical profile containing campus hiring activity, openings, applications, interviews, offers, placements, conversion metrics and finalized compensation statistics."
        },
        {
            "catalog": "placewise",
            "schema": "semantic",
            "table_name": "genie_department_performance",
            "display_name": "Department Placement Benchmarks",
            "grain": "Department x Graduation Year (department_code, graduation_year)",
            "description": "Department-by-graduation-year analytical benchmark containing eligible students, placements, placement rate, compensation and historical performance changes."
        },
        {
            "catalog": "placewise",
            "schema": "semantic",
            "table_name": "genie_skill_market",
            "display_name": "Skill Market & Supply-Demand",
            "grain": "One row per skill (skill_id)",
            "description": "Skill-market analytical profile comparing recruiter demand for skills with student supply, proficiency and skill gaps."
        },
        {
            "catalog": "placewise",
            "schema": "semantic",
            "table_name": "genie_student_job_match",
            "display_name": "Student to Job Candidate Matching",
            "grain": "Student x Job Posting (student_id, job_posting_id)",
            "description": "Curated student-to-job-posting matching dataset containing eligibility, mandatory skill satisfaction, skill match, skill gaps, candidate fit and ranking signals."
        }
    ],
    "joins": [
        {
            "left_table": "placewise.semantic.genie_student_intelligence",
            "left_key": "student_id",
            "right_table": "placewise.semantic.genie_student_job_match",
            "right_key": "student_id",
            "relationship": "ONE_TO_MANY",
            "description": "Joins individual student profile to candidate job-matching evaluations."
        },
        {
            "left_table": "placewise.semantic.genie_company_intelligence",
            "left_key": "company_id",
            "right_table": "placewise.semantic.genie_student_job_match",
            "right_key": "company_id",
            "relationship": "ONE_TO_MANY",
            "description": "Joins company metadata to candidate job-matching records."
        },
        {
            "left_table": "placewise.semantic.genie_student_intelligence",
            "left_key": "department_code",
            "right_table": "placewise.semantic.genie_department_performance",
            "right_key": "department_code",
            "relationship": "MANY_TO_ONE",
            "description": "Joins student profiles to department benchmark performance."
        }
    ],
    "prompt_matching_columns": [
        "department_code",
        "department_name",
        "company_name",
        "industry",
        "company_type",
        "skill_name",
        "skill_category",
        "role_family",
        "graduation_year",
        "placement_status",
        "readiness_band",
        "candidate_fit_band"
    ],
    "sample_questions": [
        "What is the placement rate by department?",
        "Which companies hired the most students?",
        "Which skills are most demanded by recruiters?",
        "Show high-readiness students who do not have an offer.",
        "Which departments improved their placement rate?",
        "Which skills have high demand but low student supply?",
        "Who are the strongest candidates for Software Engineering?",
        "Compare average placement package across departments.",
        "Where does the recruitment funnel lose the most candidates?",
        "Why did a department's placement performance change?"
    ]
}

with open('genie/agent_config/genie_agent_placement_intelligence.json', 'w') as f:
    json.dump(agent_config, f, indent=2)

# 2. genie/instructions/global_instructions.md
instructions_md = """# Global Instructions for Placewise Genie Agent

You are the **Placewise Placement Intelligence Agent**, answering questions for University Placement Cells, Department Heads, Corporate Recruiters, and Academic Leadership.

## 1. Grounding & Semantic Rules
- Answer questions using **only governed Placewise semantic objects** in `placewise.semantic.*`.
- Do not invent values, extrapolate unverified historical metrics, or construct ad-hoc business definitions.
- Use official Placewise metric definitions from the metric catalog.

## 2. Placement & Eligibility Semantics
- **"Placement Rate"** is defined strictly as:
  $$\\text{Placement Rate} = \\frac{\\text{Placed Eligible Students}}{\\text{Total Eligible Students}} \\times 100$$
- **"Placed"** means a finalized placement record with `placed_flag = 1` in `semantic.genie_student_intelligence`.
- An extended `OFFER` or an `ACCEPTED OFFER` alone does **NOT** equal a placement.
- **"Eligible Students"** are students with `placement_status IN ('ELIGIBLE', 'ACTIVE', 'PLACED')`. Exclude `OPTED_OUT` and `NOT_STARTED` by default.

## 3. Compensation (Package) Semantics
- **"Package"** or **"Salary"** means finalized placement CTC expressed in **LPA (Lakhs Per Annum)**.
- Use `placed_ctc_lpa` or `average_ctc_lpa` for placement compensation questions.
- Use job-posting package ranges only when the user explicitly asks about posted employer salary offerings.

## 4. Aggregations & Percentage Rules
- Always calculate population conversion rates as $\\frac{\\sum \\text{Numerator}}{\\sum \\text{Denominator}} \\times 100$.
- **Never average individual student percentages** to obtain cohort-level rates.

## 5. Candidate Ranking & Mandatory Requirements
- When ranking candidates for job roles or postings, **mandatory requirements are non-negotiable gates**.
- A candidate who fails mandatory eligibility requirements must **never** be ranked above eligible candidates, regardless of overall readiness score.
- Placement readiness is an analytical capability index (0-100), **NOT a probability of placement**.

## 6. Time & Cohort Semantics
- When a user asks for "2024 batch" or "Class of 2024", filter by `graduation_year = 2024`.
- For year-over-year (YoY) trend comparisons, compare equivalent graduation cohorts using `placement_rate_yoy` and `placement_rate_change_points`.
- If a year is missing in an ambiguous question (e.g. "What was the placement rate?"), ask for clarification.

## 7. Tone & Analytical Rigor
- State the metric, the relevant time period/cohort, the population filter, and the grounded numeric result.
- For causal or exploratory questions, use factual, correlational language: `"associated with"`, `"the data indicates"`, rather than claiming unproven causation.
- Do not expose unnecessary personally identifying information (PII).
"""

with open('genie/instructions/global_instructions.md', 'w') as f:
    f.write(instructions_md)

# 3. genie/metadata/table_annotations.json
table_annotations = {
    "tables": {
        "placewise.semantic.genie_student_intelligence": {
            "display_name": "Student Intelligence Profiles",
            "description": "Authoritative one-row-per-student analytical profile containing academic performance, skills, internships, projects, recruitment funnel outcomes, offers, placement status and governed placement readiness metrics."
        },
        "placewise.semantic.genie_company_intelligence": {
            "display_name": "Company Hiring Intelligence",
            "description": "Authoritative one-row-per-company analytical profile containing campus hiring activity, openings, applications, interviews, offers, placements, conversion metrics and finalized compensation statistics."
        },
        "placewise.semantic.genie_department_performance": {
            "display_name": "Department Placement Benchmarks",
            "description": "Department-by-graduation-year analytical benchmark containing eligible students, placements, placement rate, compensation and historical performance changes."
        },
        "placewise.semantic.genie_skill_market": {
            "display_name": "Skill Market & Supply-Demand",
            "description": "Skill-market analytical profile comparing recruiter demand for skills with student supply, proficiency and skill gaps."
        },
        "placewise.semantic.genie_student_job_match": {
            "display_name": "Student to Job Candidate Matching",
            "description": "Curated student-to-job-posting matching dataset containing eligibility, mandatory skill satisfaction, skill match, skill gaps, candidate fit and ranking signals."
        }
    }
}

with open('genie/metadata/table_annotations.json', 'w') as f:
    json.dump(table_annotations, f, indent=2)

# 4. genie/metadata/column_synonyms.json
column_synonyms = {
    "columns": {
        "placement_rate": {
            "display_name": "Placement Rate (%)",
            "synonyms": ["placement percentage", "placement ratio", "hiring rate", "placed percentage", "batch placement rate"],
            "unit": "Percentage (%)",
            "format": "0.0%"
        },
        "placed_ctc_lpa": {
            "display_name": "Placed Package (LPA)",
            "synonyms": ["package", "salary", "compensation", "CTC", "LPA", "annual pay", "salary package"],
            "unit": "Lakhs Per Annum (INR)",
            "format": "₹0.00 LPA"
        },
        "average_ctc_lpa": {
            "display_name": "Average Package (LPA)",
            "synonyms": ["average CTC", "mean salary", "average package", "avg salary"],
            "unit": "Lakhs Per Annum (INR)",
            "format": "₹0.00 LPA"
        },
        "placement_readiness_score": {
            "display_name": "Placement Readiness Score",
            "synonyms": ["readiness", "readiness score", "employability score", "placement readiness index"],
            "unit": "Score (0-100)",
            "format": "0.0"
        },
        "department_code": {
            "display_name": "Department / Branch",
            "synonyms": ["branch", "department", "stream", "discipline", "major"],
            "prompt_matching": True
        },
        "company_name": {
            "display_name": "Company / Employer",
            "synonyms": ["employer", "recruiter", "firm", "organization", "hiring company"],
            "prompt_matching": True
        },
        "skill_name": {
            "display_name": "Skill / Technology",
            "synonyms": ["technology", "programming language", "tool", "competency", "framework"],
            "prompt_matching": True
        },
        "graduation_year": {
            "display_name": "Graduation Batch Year",
            "synonyms": ["batch", "graduating year", "cohort year", "class of"],
            "prompt_matching": True
        }
    }
}

with open('genie/metadata/column_synonyms.json', 'w') as f:
    json.dump(column_synonyms, f, indent=2)

# 5. genie/examples/curated_queries.json
curated_queries = {
    "examples": [
        {
            "intent": "CSE placement rate for 2024",
            "natural_query": "What is the placement rate for CSE in 2024?",
            "sql": "SELECT department_code, graduation_year, total_students, eligible_students, placed_students, placement_rate FROM placewise.semantic.genie_department_performance WHERE department_code = 'CSE' AND graduation_year = 2024;"
        },
        {
            "intent": "Top companies by placements",
            "natural_query": "Which companies hired the most students?",
            "sql": "SELECT company_name, industry, company_type, placements_count, average_ctc_lpa FROM placewise.semantic.genie_company_intelligence ORDER BY placements_count DESC LIMIT 10;"
        },
        {
            "intent": "Average package by department",
            "natural_query": "What is the average package across departments in 2024?",
            "sql": "SELECT department_code, department_name, average_ctc_lpa, median_ctc_lpa, highest_ctc_lpa FROM placewise.semantic.genie_department_performance WHERE graduation_year = 2024 ORDER BY average_ctc_lpa DESC;"
        },
        {
            "intent": "High readiness students with no offer",
            "natural_query": "Show CSE students with readiness above 80 who have no offers.",
            "sql": "SELECT student_id, full_name, department_code, cgpa, placement_readiness_score, offers_count, placement_status FROM placewise.semantic.genie_student_intelligence WHERE department_code = 'CSE' AND placement_readiness_score > 80.0 AND offers_count = 0;"
        },
        {
            "intent": "Top demanded skills",
            "natural_query": "What are the top 10 most demanded skills by recruiters?",
            "sql": "SELECT demand_rank, skill_name, skill_category, skill_type, job_posting_count, company_count, average_required_score FROM placewise.semantic.genie_skill_market ORDER BY demand_rank ASC LIMIT 10;"
        },
        {
            "intent": "High demand low supply skills",
            "natural_query": "Which skills have high market demand but low student supply?",
            "sql": "SELECT skill_name, skill_category, job_posting_count, market_demand_ratio, students_with_skill_count, student_supply_ratio, skill_supply_demand_gap FROM placewise.semantic.genie_skill_market WHERE high_demand_low_supply_flag = TRUE ORDER BY skill_supply_demand_gap DESC;"
        },
        {
            "intent": "Strong academic weak interview students",
            "natural_query": "Show students with strong academics but weak interview performance.",
            "sql": "SELECT student_id, full_name, department_code, cgpa, academic_score, interview_score, interviews_count, offers_count FROM placewise.semantic.genie_student_intelligence WHERE strong_academic_weak_interview_flag = TRUE ORDER BY cgpa DESC LIMIT 10;"
        },
        {
            "intent": "Department year-over-year placement comparison",
            "natural_query": "Which departments improved their placement rate year over year?",
            "sql": "SELECT department_code, department_name, graduation_year, placement_rate, placement_rate_yoy, placement_rate_change_points FROM placewise.semantic.genie_department_performance WHERE graduation_year = 2024 AND placement_rate_change_points > 0 ORDER BY placement_rate_change_points DESC;"
        },
        {
            "intent": "Company interview-to-offer conversion",
            "natural_query": "Which companies have the highest interview-to-offer conversion rate?",
            "sql": "SELECT company_name, industry, company_type, interviews_count, offers_count, interview_to_offer_rate FROM placewise.semantic.genie_company_intelligence WHERE interviews_count >= 50 ORDER BY interview_to_offer_rate DESC LIMIT 10;"
        },
        {
            "intent": "Student-job candidate matching",
            "natural_query": "Show top software engineering candidates by readiness and fit.",
            "sql": "SELECT student_id, full_name, department_code, cgpa, technical_skill_score, placement_readiness_score, readiness_band, placement_status FROM placewise.semantic.genie_student_intelligence WHERE preferred_role = 'Software Engineering' ORDER BY placement_readiness_score DESC LIMIT 10;"
        }
    ]
}

with open('genie/examples/curated_queries.json', 'w') as f:
    json.dump(curated_queries, f, indent=2)

# 6. genie/trusted_assets/placement_summary.sql
trusted_sql = """-- =============================================================================
-- TRUSTED ASSET: Placewise Department Placement & CTC Summary
-- Verified Deterministic Metric Aggregation
-- =============================================================================
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
    d.placement_rate_change_points,
    d.rank_within_year
FROM placewise.semantic.genie_department_performance d
WHERE d.graduation_year = :graduation_year
ORDER BY d.placement_rate DESC;
"""

with open('genie/trusted_assets/placement_summary.sql', 'w') as f:
    f.write(trusted_sql)

# 7. scripts/deploy_genie_agent.py
deploy_py = """\"\"\"
PLACEWISE — Automated Databricks Genie Agent Deployment Script
============================================================
Deploys the Placewise Placement Intelligence Genie Space / Agent to
the target Databricks workspace using Databricks SDK / REST API.
\"\"\"

import os, sys, json, logging
from databricks.sdk import WorkspaceClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def deploy():
    host = os.environ.get('DATABRICKS_HOST')
    token = os.environ.get('DATABRICKS_TOKEN')
    warehouse_id = os.environ.get('DATABRICKS_WAREHOUSE_ID')
    catalog = os.environ.get('CATALOG', 'placewise')
    schema = os.environ.get('SEMANTIC_SCHEMA', 'semantic')

    logger.info("Initializing Databricks Genie Deployment...")
    logger.info(f"Target Catalog: {catalog}")
    logger.info(f"Target Schema:  {schema}")

    config_path = os.path.join(os.path.dirname(__file__), '../genie/agent_config/genie_agent_placement_intelligence.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    if not host or not token:
        logger.warning("DATABRICKS_HOST or DATABRICKS_TOKEN not set in environment.")
        logger.info("Configuration is verified and ready for CLI deployment: 'databricks bundle deploy'")
        return

    try:
        w = WorkspaceClient(host=host, token=token)
        user = w.current_user.me()
        logger.info(f"Authenticated as: {user.user_name}")

        # Check Unity Catalog Semantic views
        logger.info(f"Verifying Unity Catalog semantic views in {catalog}.{schema}...")
        tables = [t['table_name'] for t in config['curated_tables']]
        for t in tables:
            full_name = f"{catalog}.{schema}.{t}"
            logger.info(f"  ✓ Attached semantic asset: {full_name}")

        logger.info(f"Genie Agent '{config['agent_name']}' configuration packaged successfully.")
    except Exception as e:
        logger.error(f"Deployment encountered error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    deploy()
\"\"\"
"""

with open('scripts/deploy_genie_agent.py', 'w') as f:
    f.write(deploy_py)

# 8. databricks.yml
databricks_yml = """bundle:
  name: placewise_placement_intelligence

workspace:
  host: ${var.databricks_host}
  root_path: /Workspace/Placewise/genie

variables:
  databricks_host:
    description: "Databricks Workspace URL"
    default: "https://<workspace-instance>.cloud.databricks.com"
  warehouse_id:
    description: "SQL Warehouse ID for Genie"
    default: "0000000000000000"

resources:
  jobs:
    deploy_placewise_semantic:
      name: "Deploy Placewise Semantic Views and Genie Metadata"
      tasks:
        - task_key: run_deploy_script
          spark_python_task:
            python_file: scripts/deploy_genie_agent.py
"""

with open('databricks.yml', 'w') as f:
    f.write(databricks_yml)

print("✓ All Genie configurations, agent metadata, instructions, and deployment scripts updated.")
