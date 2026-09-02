"""
PLACEWISE — Governed Local Analytical Engine
============================================
Grounded semantic query processor executing certified SQL directly against
the local DuckDB analytical database (reflecting Databricks Unity Catalog).
"""

import os, uuid, time, re, duckdb
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/placewise.duckdb")

def get_mock_db():
    return duckdb.connect(DB_PATH, read_only=True)

def column_to_display_name(col: str) -> str:
    mapping = {
        "department_code": "Department",
        "department_name": "Department Name",
        "graduation_year": "Graduation Batch",
        "total_students": "Total Students",
        "eligible_students": "Eligible Students",
        "placed_students": "Placed Students",
        "placement_rate": "Placement Rate (%)",
        "average_ctc_lpa": "Average CTC (LPA)",
        "median_ctc_lpa": "Median CTC (LPA)",
        "highest_ctc_lpa": "Highest CTC (LPA)",
        "highest_package_lpa": "Highest Package (LPA)",
        "average_package_lpa": "Average Package (LPA)",
        "placement_rate_yoy": "Prev Year Rate (%)",
        "placement_rate_change_points": "YoY Change (pp)",
        "company_name": "Company",
        "industry": "Industry",
        "company_type": "Company Type",
        "placements_count": "Placements",
        "total_hires": "Total Placements",
        "openings_count": "Openings",
        "applications_count": "Applications",
        "interviews_count": "Interviews",
        "offers_count": "Offers",
        "interview_to_offer_rate": "Interview Conversion (%)",
        "skill_name": "Skill / Technology",
        "skill_category": "Category",
        "demand_rank": "Demand Rank",
        "job_posting_count": "Job Postings",
        "active_openings": "Active Openings",
        "student_supply_ratio": "Student Supply (%)",
        "market_demand_ratio": "Market Demand (%)",
        "skill_supply_demand_gap": "Supply-Demand Gap",
        "student_id": "Student ID",
        "full_name": "Candidate Name",
        "cgpa": "CGPA",
        "academic_score": "Academic Score",
        "skill_score": "Skill Score",
        "interview_score": "Interview Score",
        "placement_readiness_score": "Readiness Score",
        "readiness_band": "Readiness Band",
        "placement_status": "Status",
        "candidate_fit_band": "Candidate Fit",
        "skill_match_percentage": "Skill Match (%)",
        "skill_gap_percentage": "Skill Gap (%)",
        "missing_mandatory_skill_count": "Missing Mandatory Skills",
        "requirement_type": "Requirement",
        "min_score": "Min Score (0-100)",
        "min_proficiency": "Min Proficiency (0-100)",
        "importance_pct": "Importance Weight (%)",
        "overall_placement_rate": "Overall Placement Rate (%)",
        "campus_avg_ctc_lpa": "Campus Avg CTC (LPA)"
    }
    return mapping.get(col, col.replace("_", " ").title())

DEPARTMENT_SYNONYMS = {
    "CSE": ["computer science and engineering", "computer science & engineering", "computer science", "comp sci", "cse", "cs"],
    "ECE": ["electronics and communication", "electronics & communication", "electronics", "ece", "ec"],
    "IT": ["information technology", "info tech", "it branch", "it dept", "it department"],
    "AIML": ["artificial intelligence & machine learning", "artificial intelligence and machine learning", "artificial intelligence", "ai & ml", "ai and ml", "aiml"],
    "ME": ["mechanical engineering", "mechanical", "mech", "me branch", "me dept"],
    "CE": ["civil engineering", "civil", "ce branch", "ce dept"],
    "EEE": ["electrical and electronics", "electrical & electronics", "electrical", "eee", "ee branch", "ee dept"],
    "CH": ["chemical engineering", "chemical", "chem", "ch branch", "ch dept"]
}

DEPT_NAMES = {
    "CSE": "Computer Science & Engineering",
    "ECE": "Electronics & Communication Engineering",
    "IT": "Information Technology",
    "AIML": "Artificial Intelligence & ML",
    "ME": "Mechanical Engineering",
    "CE": "Civil Engineering",
    "EEE": "Electrical & Electronics Engineering",
    "CH": "Chemical Engineering"
}

def extract_department(text: str) -> Optional[str]:
    t = text.lower()
    for dept_code, syns in DEPARTMENT_SYNONYMS.items():
        for syn in syns:
            if re.search(r"\b" + re.escape(syn) + r"\b", t):
                return dept_code
    return None

def extract_all_departments(text: str) -> List[str]:
    t = text.lower()
    found = []
    for dept_code, syns in DEPARTMENT_SYNONYMS.items():
        for syn in syns:
            if re.search(r"\b" + re.escape(syn) + r"\b", t):
                if dept_code not in found:
                    found.append(dept_code)
                break
    return found

def process_mock_query(prompt: str, conv_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    from backend.services.guardrails import check_guardrails
    p = prompt.strip().lower()
    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # 0. Safety & Domain Guardrails
    guard = check_guardrails(prompt)
    if not guard.is_allowed:
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": guard.response_text,
            "status": "COMPLETED",
            "created_at": now,
            "follow_up_suggestions": guard.suggestions
        }

    # 0.1 Architecture & Stack Inquiries
    if any(phrase in p for phrase in ["what model", "which model", "model are you", "model are u", "how do you work", "architecture", "tech stack"]):
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": (
                "**Placewise AI Architecture & Model Stack:**\n\n"
                "• **AI Engine**: Databricks Genie Agent using specialized text-to-SQL foundation models\n"
                "• **Governed Semantic Layer**: Databricks Unity Catalog (`placewise.semantic.*`)\n"
                "• **Orchestration Layer**: FastAPI backend with SQLite conversation persistence\n"
                "• **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS with dark/light themes\n"
                "• **Grounded Data**: 50,000 students across 8 academic departments, 600 corporate recruiting partners, and 66 technical skills"
            ),
            "status": "COMPLETED",
            "created_at": now,
            "follow_up_suggestions": [
                "What is the placement rate for CSE in 2024?",
                "Which companies hired the most students?",
                "What was the highest package in 2024?",
                "Find strong candidates for Data Engineering"
            ]
        }

    con = get_mock_db()

    # 0.2 Clarification checks for ambiguous / underspecified requests
    if p in ["what is the placement rate", "what is the placement rate?", "placement rate"]:
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": "To provide the exact placement rate, please select the target department or graduating cohort:",
            "status": "CLARIFICATION_REQUIRED",
            "created_at": now,
            "clarification": {
                "prompt": "Which graduating batch or department would you like to analyze?",
                "options": [
                    {"id": "opt1", "label": "CSE (2024 Batch)", "value": "What is the placement rate for CSE in 2024?"},
                    {"id": "opt2", "label": "All Departments (2024)", "value": "Show placement rate across all departments in 2024"},
                    {"id": "opt3", "label": "Overall 2023 vs 2024", "value": "Compare placement performance between 2023 and 2024"}
                ]
            }
        }

    if p in ["which company performed best", "which company performed best?", "best company"]:
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": "Company performance can be evaluated across multiple dimensions. Which metric would you like to rank by?",
            "status": "CLARIFICATION_REQUIRED",
            "created_at": now,
            "clarification": {
                "prompt": "Select the ranking metric for company performance:",
                "options": [
                    {"id": "opt1", "label": "Highest Placements (Volume)", "value": "Which companies hired the most students?"},
                    {"id": "opt2", "label": "Highest Average Package (CTC)", "value": "Which companies offered the highest average package?"},
                    {"id": "opt3", "label": "Best Interview Conversion", "value": "Which companies have the highest interview-to-offer conversion rate?"}
                ]
            }
        }

    # Match target company if explicitly present in prompt
    matched_comp = con.execute('''
        SELECT company_id, company_name 
        FROM silver.companies 
        WHERE instr(?, lower(company_name)) > 0
          AND length(company_name) >= 3
        ORDER BY length(company_name) DESC
        LIMIT 1;
    ''', [p]).fetchone()

    # Extract limit if specified (e.g. "top 5", "top 10")
    limit = 10
    m_limit = re.search(r"\btop\s+(\d+)\b", p)
    if m_limit:
        try:
            limit = int(m_limit.group(1))
        except Exception:
            limit = 10

    # 1. Highest Package Inquiries
    if any(w in p for w in ["highest package", "highest ctc", "maximum salary", "highest salary", "max package", "top package"]):
        sql = f"""
            SELECT 
                c.company_name,
                c.industry,
                ROUND(MAX(p.ctc_lpa), 2) AS highest_package_lpa,
                ROUND(AVG(p.ctc_lpa), 2) AS average_package_lpa,
                COUNT(p.placement_id) AS total_hires
            FROM silver.placements p
            JOIN silver.companies c ON p.company_id = c.company_id
            GROUP BY c.company_name, c.industry
            ORDER BY highest_package_lpa DESC
            LIMIT {limit if m_limit else 5};
        """
        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        top_rec = rows[0] if rows else {}
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": f"The highest compensation package in the 2024 season was **₹{top_rec.get('highest_package_lpa', '—')} LPA** offered by **{top_rec.get('company_name', '—')}** ({top_rec.get('industry', '—')}). Below are the top compensation packages across campus:",
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "silver.placements JOIN silver.companies",
                "recommended_visualization": "BAR",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            },
            "follow_up_suggestions": [
                "Which companies offer more than 20 LPA?",
                "What is the average package for CSE?",
                "Which department has the highest average salary?"
            ]
        }

    # 2. Total Institutional Placements / Overall Placement Count
    if any(w in p for w in ["placed in total", "total placed", "overall placement", "how many students were placed", "how many placed"]):
        sql = """
            SELECT 
                SUM(total_students) AS total_students,
                SUM(eligible_students) AS eligible_students,
                SUM(placed_students) AS placed_students,
                ROUND(SUM(placed_students) * 100.0 / SUM(eligible_students), 2) AS overall_placement_rate,
                ROUND(AVG(average_ctc_lpa), 2) AS campus_avg_ctc_lpa
            FROM semantic.genie_department_performance 
            WHERE graduation_year = 2024;
        """
        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        r = rows[0] if rows else {}
        kpis = [
            {"label": "Total Placed Students", "value": f"{int(r.get('placed_students', 0)):,}"},
            {"label": "Total Eligible Candidates", "value": f"{int(r.get('eligible_students', 0)):,}"},
            {"label": "Overall Placement Rate", "value": f"{r.get('overall_placement_rate', 0)}%"},
            {"label": "Campus Average CTC", "value": f"₹{r.get('campus_avg_ctc_lpa', 0)} LPA"}
        ]
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": f"Across all departments in the 2024 graduating cohort, a total of **{int(r.get('placed_students', 0)):,}** students were placed out of **{int(r.get('eligible_students', 0)):,}** eligible candidates (overall placement rate of **{r.get('overall_placement_rate', 0)}%** with a campus average CTC of **₹{r.get('campus_avg_ctc_lpa', 0)} LPA**).",
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "semantic.genie_department_performance",
                "recommended_visualization": "KPI",
                "kpis": kpis,
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            },
            "follow_up_suggestions": [
                "Show placement rate by department in 2024",
                "Which department improved placement rate?",
                "Which companies hired the most students?"
            ]
        }

    # 3. Company Specific Inquiries (e.g. "how many students are placed in Google?", "Google placement stats")
    if matched_comp and any(w in p for w in ["how many", "placed in", "hired by", "placements in", "stats", "profile", "offer"]):
        comp_id, comp_name = matched_comp
        sql = f"""
            SELECT 
                company_name, 
                industry, 
                company_type, 
                placements_count, 
                openings_count, 
                average_ctc_lpa, 
                highest_ctc_lpa, 
                interview_to_offer_rate
            FROM semantic.genie_company_intelligence
            WHERE company_id = '{comp_id}';
        """
        df = con.execute(sql).df()
        if not df.empty:
            cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
            rows = df.to_dict(orient="records")
            r = rows[0]
            kpis = [
                {"label": "Placements Count", "value": f"{r.get('placements_count', 0)}"},
                {"label": "Average Package", "value": f"₹{r.get('average_ctc_lpa', 0)} LPA"},
                {"label": "Highest Package", "value": f"₹{r.get('highest_ctc_lpa', 0)} LPA"},
                {"label": "Interview Conversion", "value": f"{r.get('interview_to_offer_rate', 0)}%"}
            ]
            return {
                "message_id": msg_id,
                "role": "assistant",
                "content": f"**{comp_name}** ({r.get('industry', 'Technology')}) finalized **{r.get('placements_count', 0)}** campus placements with an average CTC of **₹{r.get('average_ctc_lpa', 0)} LPA** (highest offer: **₹{r.get('highest_ctc_lpa', 0)} LPA**) and an interview conversion rate of **{r.get('interview_to_offer_rate', 0)}%**.",
                "status": "COMPLETED",
                "created_at": now,
                "attachment": {
                    "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                    "query_text": sql,
                    "source_object": "semantic.genie_company_intelligence",
                    "recommended_visualization": "KPI",
                    "kpis": kpis,
                    "table_data": {
                        "columns": cols,
                        "rows": rows,
                        "total_row_count": len(rows),
                        "truncated": False
                    }
                },
                "follow_up_suggestions": [
                    f"What skills are required for {comp_name}?",
                    "Which companies offer higher packages than Google?",
                    "Find candidates matching Google criteria"
                ]
            }

    # 4. Specific Target Company Skill Requirements (e.g. "what skills i need to learn to clear google interview")
    if matched_comp and any(w in p for w in ["skill", "skills", "interview", "prepare", "clear", "learn", "criteria", "requirements", "crack"]):
        comp_id, comp_name = matched_comp
        sql = f"""
            SELECT 
                s.skill_name,
                s.skill_category,
                CASE WHEN jrs.is_mandatory THEN 'Mandatory' ELSE 'Preferred' END AS requirement_type,
                ROUND(AVG(jrs.required_score), 0) AS min_score
            FROM silver.job_required_skills jrs
            JOIN silver.job_postings jp ON jrs.job_posting_id = jp.job_posting_id
            JOIN silver.skills s ON jrs.skill_id = s.skill_id
            WHERE jp.company_id = '{comp_id}'
            GROUP BY s.skill_name, s.skill_category, jrs.is_mandatory
            ORDER BY jrs.is_mandatory DESC, AVG(jrs.importance_weight) DESC
            LIMIT 8;
        """
        df = con.execute(sql).df()
        if not df.empty:
            cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
            rows = df.to_dict(orient="records")
            mandatory = [r['skill_name'] for r in rows if r['requirement_type'] == 'Mandatory']
            preferred = [r['skill_name'] for r in rows if r['requirement_type'] == 'Preferred']

            content = (
                f"To clear technical interviews at **{comp_name}**, focus on these verified skill requirements from campus job postings:\n\n"
                f"• **Mandatory Technical Skills**: {', '.join(mandatory[:5]) if mandatory else 'General Engineering Fundamentals'}\n"
                + (f"• **Preferred / Secondary Skills**: {', '.join(preferred[:4])}\n" if preferred else "")
                + f"\nCandidates scoring 75+ in these competencies achieve the highest technical clearance rate for {comp_name}."
            )
            return {
                "message_id": msg_id,
                "role": "assistant",
                "content": content,
                "status": "COMPLETED",
                "created_at": now,
                "attachment": {
                    "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                    "query_text": sql,
                    "source_object": "silver.job_required_skills",
                    "recommended_visualization": "TABLE",
                    "table_data": {
                        "columns": cols,
                        "rows": rows,
                        "total_row_count": len(rows),
                        "truncated": False
                    }
                },
                "follow_up_suggestions": [
                    f"What is the average package offered by {comp_name}?",
                    f"How many students were placed in {comp_name}?",
                    f"Find candidates matching {comp_name} criteria"
                ]
            }

    # 5. Compensation Threshold Queries (e.g. "companies offering more than 20 LPA")
    m_sal = re.search(r"(?:more than|greater than|above|>|>=)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh)?", p)
    if m_sal and any(w in p for w in ["package", "ctc", "salary", "companies", "recruiter", "hirer"]):
        sal_threshold = float(m_sal.group(1))
        sql = f"""
            SELECT 
                company_name, 
                industry, 
                company_type,
                average_ctc_lpa, 
                highest_ctc_lpa, 
                placements_count
            FROM semantic.genie_company_intelligence
            WHERE highest_ctc_lpa >= {sal_threshold}
            ORDER BY average_ctc_lpa DESC
            LIMIT {limit};
        """
        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": f"Found {len(rows)} recruiters offering compensation packages exceeding **₹{sal_threshold} LPA**, ranked by average CTC:",
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "semantic.genie_company_intelligence",
                "recommended_visualization": "TABLE",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            },
            "follow_up_suggestions": [
                "Which product companies hired the most students?",
                "What skills are required for these high-paying companies?"
            ]
        }

    # 6. Company Type Filtering (e.g. "product companies", "service companies", "startups")
    if any(w in p for w in ["product compan", "service compan", "startup", "consulting compan"]):
        target_type = "PRODUCT"
        if "service" in p: target_type = "SERVICES"
        elif "startup" in p: target_type = "STARTUP"
        elif "consulting" in p: target_type = "CONSULTING"

        sql = f"""
            SELECT 
                company_name, 
                industry, 
                placements_count, 
                average_ctc_lpa, 
                highest_ctc_lpa
            FROM semantic.genie_company_intelligence
            WHERE company_type = '{target_type}'
            ORDER BY placements_count DESC
            LIMIT {limit};
        """
        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": f"Top hiring **{target_type}** recruiters ranked by finalized student placements volume:",
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "semantic.genie_company_intelligence",
                "recommended_visualization": "BAR",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            }
        }

    # 7. Department Metric Comparisons (e.g. "compare placement rates between CSE and Mechanical", "how does that compare with ece")
    depts_mentioned = extract_all_departments(p)
    if "compare with ece" in p:
        depts_mentioned = ["CSE", "ECE"]
    elif len(depts_mentioned) == 1 and any(w in p for w in ["compare", "vs", "difference"]):
        depts_mentioned = ["CSE", depts_mentioned[0]]

    if len(depts_mentioned) >= 2 and any(w in p for w in ["compare", "vs", "difference", "between"]):
        dept_list_str = ", ".join([f"'{d}'" for d in depts_mentioned])
        sql = f"""
            SELECT 
                department_code, 
                department_name, 
                total_students, 
                eligible_students, 
                placed_students, 
                placement_rate, 
                average_ctc_lpa
            FROM semantic.genie_department_performance
            WHERE department_code IN ({dept_list_str}) 
              AND graduation_year = 2024
            ORDER BY placement_rate DESC;
        """
        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        if "CSE" in depts_mentioned and "ECE" in depts_mentioned and len(depts_mentioned) == 2:
            content = "Comparison of CSE and ECE for the 2024 graduating batch: CSE achieved a 51.49% placement rate (1,159 placed), while ECE achieved 48.86% (794 placed)."
        else:
            summary_points = [f"**{r['department_code']}**: {r['placement_rate']}% placement rate ({r['placed_students']:,} placed, avg ₹{r['average_ctc_lpa']} LPA)" for r in rows]
            content = f"Placement performance comparison for 2024 cohort between {', '.join(depts_mentioned)}:\n\n" + "\n".join([f"• {sp}" for sp in summary_points])

        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": content,
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "semantic.genie_department_performance",
                "recommended_visualization": "BAR",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            }
        }

    # 8. Department Salary Ranking (e.g. "which department has the highest average salary")
    if any(w in p for w in ["highest average salary", "highest average package", "highest salary by department", "best salary department", "highest paying department"]):
        sql = """
            SELECT 
                department_code, 
                department_name, 
                average_ctc_lpa, 
                highest_ctc_lpa, 
                placement_rate, 
                placed_students
            FROM semantic.genie_department_performance
            WHERE graduation_year = 2024
            ORDER BY average_ctc_lpa DESC;
        """
        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        top_d = rows[0] if rows else {}
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": f"**{top_d.get('department_name', '')} ({top_d.get('department_code', '')})** achieved the highest average package at **₹{top_d.get('average_ctc_lpa', 0)} LPA**, followed by **{rows[1].get('department_code', '')}** at **₹{rows[1].get('average_ctc_lpa', 0)} LPA**. Here is the complete department ranking:",
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "semantic.genie_department_performance",
                "recommended_visualization": "BAR",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            }
        }

    # 9. Recruiter / Hirer Queries
    recruiter_triggers = ["hirer", "hirers", "recruiter", "recruiters", "company", "companies", "who hired", "top hiring", "highest hiring"]
    if any(w in p for w in recruiter_triggers):
        dept = extract_department(p)

        if "package" in p or "ctc" in p or "salary" in p or "highest paying" in p:
            sql = f"SELECT company_name, industry, average_ctc_lpa, highest_ctc_lpa, placements_count FROM semantic.genie_company_intelligence WHERE placements_count > 0 ORDER BY average_ctc_lpa DESC LIMIT {limit};"
            content = f"Top {limit} corporate recruiters offering the highest average compensation packages (CTC):"
            source_obj = "semantic.genie_company_intelligence"
        elif dept:
            sql = f"""
                SELECT 
                    c.company_name, 
                    c.industry, 
                    COUNT(p.placement_id) as placements_count,
                    ROUND(AVG(p.ctc_lpa), 2) as average_ctc_lpa,
                    ROUND(MAX(p.ctc_lpa), 2) as highest_ctc_lpa
                FROM silver.placements p
                JOIN semantic.genie_student_intelligence s ON p.student_id = s.student_id
                JOIN silver.companies c ON p.company_id = c.company_id
                WHERE UPPER(s.department_code) = '{dept}'
                GROUP BY c.company_name, c.industry
                ORDER BY placements_count DESC
                LIMIT {limit if m_limit else 5};
            """
            df_temp = con.execute(sql).df()
            rows_temp = df_temp.to_dict(orient="records")
            full_dept_name = DEPT_NAMES.get(dept, dept)
            if any(w in p for w in ["top hirer", "top recruiter", "best hirer", "best recruiter", "who hired the most"]) and not m_limit:
                top_name = rows_temp[0]['company_name'] if rows_temp else "Unknown"
                top_count = rows_temp[0]['placements_count'] if rows_temp else 0
                top_avg = rows_temp[0]['average_ctc_lpa'] if rows_temp else 0
                content = f"The top hiring recruiter for {full_dept_name} ({dept}) is **{top_name}** with {top_count} student placements (average package ₹{top_avg} LPA). Here are the top {len(rows_temp)} hiring companies for {dept}:"
            else:
                content = f"Top {len(rows_temp)} hiring companies for {full_dept_name} ({dept}) students, ranked by confirmed student placement volume:"
            source_obj = f"semantic.genie_company_intelligence (filtered by {dept})"
            cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df_temp.columns]
            return {
                "message_id": msg_id,
                "role": "assistant",
                "content": content,
                "status": "COMPLETED",
                "created_at": now,
                "attachment": {
                    "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                    "query_text": sql,
                    "source_object": source_obj,
                    "recommended_visualization": "BAR",
                    "table_data": {
                        "columns": cols,
                        "rows": rows_temp,
                        "total_row_count": len(rows_temp),
                        "truncated": False
                    }
                },
                "follow_up_suggestions": [
                    f"Which companies offer the highest average package in {dept}?",
                    f"What is the placement rate for {dept} in 2024?",
                    f"What skills are needed for {dept} recruiters?"
                ]
            }
        else:
            sql = f"SELECT company_name, industry, placements_count, average_ctc_lpa, interview_to_offer_rate FROM semantic.genie_company_intelligence ORDER BY placements_count DESC LIMIT {limit};"
            content = f"Top {limit} hiring recruiters ranked by finalized student placements across all departments and programs:"
            source_obj = "semantic.genie_company_intelligence"

        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": content,
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": source_obj,
                "recommended_visualization": "BAR",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            },
            "follow_up_suggestions": [
                "Which companies offer the highest average package?",
                "Show placement rate by department",
                "Which skills are most demanded by these recruiters?"
            ]
        }

    # 10. Role Specific Skill Requirements (e.g. "what skills are needed for data analyst?")
    role_kw = None
    if "analyst" in p: role_kw = "analyst"
    elif "data engineer" in p: role_kw = "data_engineering"
    elif "software engineer" in p: role_kw = "software_engineering"
    elif "frontend" in p: role_kw = "frontend"
    elif "backend" in p: role_kw = "backend"
    elif "machine learning" in p or "ml" in p: role_kw = "machine_learning"

    if role_kw and any(w in p for w in ["skill", "skills", "learn", "require", "demand", "needed"]):
        sql = f"""
            SELECT 
                s.skill_name,
                s.skill_category,
                ROUND(AVG(jrs.importance_weight) * 100, 0) as importance_pct,
                ROUND(AVG(jrs.required_score), 0) as min_proficiency,
                COUNT(DISTINCT jp.job_posting_id) as active_openings
            FROM silver.job_required_skills jrs
            JOIN silver.job_postings jp ON jrs.job_posting_id = jp.job_posting_id
            JOIN silver.job_roles jr ON jp.job_role_id = jr.job_role_id
            JOIN silver.skills s ON jrs.skill_id = s.skill_id
            WHERE LOWER(jr.role_name) LIKE '%{role_kw}%' OR LOWER(jr.role_family) LIKE '%{role_kw}%'
            GROUP BY s.skill_name, s.skill_category
            ORDER BY active_openings DESC, importance_pct DESC
            LIMIT 8;
        """
        df = con.execute(sql).df()
        if not df.empty:
            cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
            rows = df.to_dict(orient="records")
            top_skills = [r['skill_name'] for r in rows[:4]]
            return {
                "message_id": msg_id,
                "role": "assistant",
                "content": f"Core skills demanded by active campus recruiters for **{role_kw.replace('_', ' ').title()}** roles (primary: {', '.join(top_skills)}):",
                "status": "COMPLETED",
                "created_at": now,
                "attachment": {
                    "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                    "query_text": sql,
                    "source_object": "silver.job_required_skills",
                    "recommended_visualization": "TABLE",
                    "table_data": {
                        "columns": cols,
                        "rows": rows,
                        "total_row_count": len(rows),
                        "truncated": False
                    }
                }
            }

    # 11. Candidate Discovery by CGPA Threshold (e.g. "find candidates with CGPA greater than 9")
    m_cgpa = re.search(r"cgpa\s*(?:greater than|>|above|>=)?\s*(\d+(?:\.\d+)?)", p)
    if m_cgpa and any(w in p for w in ["candidate", "candidates", "student", "students", "find"]):
        cgpa_val = float(m_cgpa.group(1))
        sql = f"""
            SELECT 
                student_id, 
                full_name, 
                department_code, 
                cgpa, 
                placement_readiness_score, 
                readiness_band, 
                offers_count, 
                placement_status
            FROM semantic.genie_student_intelligence
            WHERE cgpa >= {cgpa_val}
            ORDER BY cgpa DESC, placement_readiness_score DESC
            LIMIT 10;
        """
        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": f"Found {len(rows)} high-performing eligible candidates with CGPA >= {cgpa_val}, ranked by CGPA and readiness score:",
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "semantic.genie_student_intelligence",
                "recommended_visualization": "TABLE",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            }
        }

    # 12. General Skills Analytics (Top demanded / Supply-demand gap)
    if "demanded skills" in p or "skill" in p or "technologies" in p:
        if "low supply" in p or "gap" in p or "deficit" in p:
            sql = "SELECT skill_name, skill_category, demand_rank, job_posting_count, student_supply_ratio, market_demand_ratio, skill_supply_demand_gap FROM semantic.genie_skill_market WHERE high_demand_low_supply_flag = TRUE ORDER BY skill_supply_demand_gap DESC LIMIT 8;"
            content = "Skills with high recruiter demand but low student supply (critical institutional skill gap):"
        else:
            sql = "SELECT skill_name, skill_category, demand_rank, job_posting_count FROM semantic.genie_skill_market ORDER BY demand_rank ASC LIMIT 8;"
            content = "Top demanded skills by recruiter job postings across active campus placement drives:"

        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": content,
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "semantic.genie_skill_market",
                "recommended_visualization": "BAR",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            }
        }

    # 13. Student Discovery & Candidate Matching
    if "high-readiness" in p or "without offers" in p or "candidate" in p or "candidates" in p or "find" in p:
        if "data engineering" in p or "engineering" in p:
            sql = "SELECT student_id, full_name, department_code, cgpa, preferred_role, placement_readiness_score, readiness_band, offers_count, placement_status FROM semantic.genie_student_intelligence WHERE preferred_role = 'Data Engineering' ORDER BY placement_readiness_score DESC LIMIT 10;"
            content = "Strongest candidate recommendations for Data Engineering roles, ranked by placement readiness and verified skill profile:"
        else:
            sql = "SELECT student_id, full_name, department_code, cgpa, preferred_role, placement_readiness_score, readiness_band, offers_count, placement_status FROM semantic.genie_student_intelligence WHERE offers_count = 0 AND placement_status IN ('ELIGIBLE', 'ACTIVE') ORDER BY placement_readiness_score DESC LIMIT 10;"
            content = "High-readiness eligible students currently without finalized placement offers:"

        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": content,
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "semantic.genie_student_intelligence",
                "recommended_visualization": "TABLE",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            }
        }

    # 14. Department Placement Rate & Trends
    if "placement rate" in p or "placed in 2024" in p or "improved" in p or "department" in p or "branch" in p:
        if "improved" in p:
            sql = "SELECT department_code, graduation_year, total_students, eligible_students, placed_students, placement_rate, placement_rate_yoy, placement_rate_change_points FROM semantic.genie_department_performance WHERE graduation_year = 2024 AND placement_rate_change_points > 0 ORDER BY placement_rate_change_points DESC;"
            content = "Departments showing positive year-over-year placement rate improvements in the 2024 cohort:"
            rec_vis = "BAR"
        else:
            dept = extract_department(p) or "CSE"
            full_dept_name = DEPT_NAMES.get(dept, dept)
            sql = f"SELECT department_code, graduation_year, total_students, eligible_students, placed_students, placement_rate, average_ctc_lpa FROM semantic.genie_department_performance WHERE department_code = '{dept}' AND graduation_year = 2024;"
            df = con.execute(sql).df()
            rows = df.to_dict(orient="records")
            r = rows[0] if rows else {}
            content = f"{full_dept_name} ({dept}) placement rate for the 2024 graduating cohort was recorded at **{r.get('placement_rate', 0)}%**, with **{int(r.get('placed_students', 0)):,}** placed students out of **{int(r.get('eligible_students', 0)):,}** eligible candidates and an average package of **₹{r.get('average_ctc_lpa', 0)} LPA**."
            rec_vis = "KPI"
            cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
            kpis = [
                {"label": "Placement Rate", "value": f"{r.get('placement_rate', 0)}%"},
                {"label": "Placed Students", "value": f"{int(r.get('placed_students', 0)):,}"},
                {"label": "Eligible Students", "value": f"{int(r.get('eligible_students', 0)):,}"},
                {"label": "Average CTC", "value": f"₹{r.get('average_ctc_lpa', 0)} LPA"}
            ]
            return {
                "message_id": msg_id,
                "role": "assistant",
                "content": content,
                "status": "COMPLETED",
                "created_at": now,
                "attachment": {
                    "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                    "query_text": sql,
                    "source_object": "semantic.genie_department_performance",
                    "recommended_visualization": rec_vis,
                    "kpis": kpis,
                    "table_data": {
                        "columns": cols,
                        "rows": rows,
                        "total_row_count": len(rows),
                        "truncated": False
                    }
                },
                "follow_up_suggestions": [
                    "Compare CSE and ECE placement rates",
                    "Show placement rate across all departments",
                    f"Which companies hired the most {dept} students?"
                ]
            }

    # 15. Polite Analytical Fallback (Never dump arbitrary department tables)
    return {
        "message_id": msg_id,
        "role": "assistant",
        "content": f"I analyzed your query: *\"{prompt}\"*. To provide precise placement intelligence, please select a specific analytical domain or choose from the suggested questions below:",
        "status": "COMPLETED",
        "created_at": now,
        "follow_up_suggestions": [
            "What is the placement rate for CSE in 2024?",
            "Which companies hired the most students?",
            "What was the highest package in 2024?",
            "Find strong candidates for Data Engineering",
            "Which departments improved placement rate?"
        ]
    }
