"""
PLACEWISE — Offline / Development Mock Analytics Engine
=======================================================
Isolated mock query processor used during local development or unit tests
when Databricks Genie live credentials are not available or restricted by policy.
"""

import os, uuid, time, re, duckdb
from typing import List, Dict, Any

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
        "placement_rate": "Placement Rate",
        "average_ctc_lpa": "Average CTC (LPA)",
        "median_ctc_lpa": "Median CTC (LPA)",
        "highest_ctc_lpa": "Highest CTC (LPA)",
        "placement_rate_yoy": "Prev Year Rate",
        "placement_rate_change_points": "YoY Change (pp)",
        "company_name": "Company",
        "industry": "Industry",
        "company_type": "Company Type",
        "placements_count": "Placements",
        "openings_count": "Openings",
        "applications_count": "Applications",
        "interviews_count": "Interviews",
        "offers_count": "Offers",
        "interview_to_offer_rate": "Interview Conversion %",
        "skill_name": "Skill / Technology",
        "skill_category": "Category",
        "demand_rank": "Demand Rank",
        "job_posting_count": "Job Postings",
        "student_supply_ratio": "Student Supply %",
        "market_demand_ratio": "Market Demand %",
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
        "skill_match_percentage": "Skill Match %",
        "skill_gap_percentage": "Skill Gap %",
        "missing_mandatory_skill_count": "Missing Mandatory Skills",
        "requirement_type": "Requirement",
        "min_score": "Min Score (0-100)"
    }
    return mapping.get(col, col.replace("_", " ").title())

DEPARTMENT_SYNONYMS = {
    "CSE": ["computer science and engineering", "computer science & engineering", "computer science", "comp sci", "cse", "cs"],
    "ECE": ["electronics and communication", "electronics & communication", "electronics", "ece", "ec"],
    "IT": ["information technology", "info tech", "it"],
    "AIML": ["artificial intelligence & machine learning", "artificial intelligence and machine learning", "artificial intelligence", "ai & ml", "ai and ml", "aiml"],
    "ME": ["mechanical engineering", "mechanical", "mech", "me"],
    "CE": ["civil engineering", "civil", "ce"],
    "EEE": ["electrical and electronics", "electrical & electronics", "electrical", "eee", "ee"],
    "CH": ["chemical engineering", "chemical", "ch"]
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

def extract_department(text: str):
    t = text.lower()
    for dept_code, syns in DEPARTMENT_SYNONYMS.items():
        for syn in syns:
            if re.search(r"\b" + re.escape(syn) + r"\b", t):
                return dept_code
    return None

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

    # 0.1 Model / Architecture questions
    if any(phrase in p for phrase in ["what model", "which model", "model are you", "model are u", "how do you work", "architecture"]):
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": (
                "**Placewise Architecture & Model Stack:**\n\n"
                "• **AI Engine**: Databricks Genie Agent using specialized text-to-SQL foundation models\n"
                "• **Semantic & Data Layer**: Databricks Unity Catalog (`placewise.semantic.*`)\n"
                "• **Orchestration**: FastAPI backend with SQLite conversation persistence\n"
                "• **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS with dark/light themes\n"
                "• **Grounded Data**: Institutional placement profiles, department benchmarks, recruiter compensation, and candidate-job matching"
            ),
            "status": "COMPLETED",
            "created_at": now,
            "follow_up_suggestions": [
                "What is the placement rate for CSE in 2024?",
                "Which companies hired the most students?",
                "What are the top 10 demanded skills?",
                "Find strong candidates for Data Engineering"
            ]
        }

    con = get_mock_db()

    # 1. Clarification check
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

    # 2. Agent Mode Multi-Step Reasoning
    if "why did mechanical" in p or "why did me placement" in p:
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": "Mechanical Engineering placement rate declined from 68.72% in 2023 to 66.73% in 2024 (a 1.99 percentage point change). The multi-factor analysis below breaks down the primary associated drivers across recruitment volume, interview conversion, and core skill requirements.",
            "status": "COMPLETED",
            "created_at": now,
            "agent_analysis": {
                "summary": "Mechanical Engineering placement performance declined by 1.99 percentage points in the 2024 cohort, driven primarily by lower core interview conversion and reduced manufacturing drive openings.",
                "findings": [
                    "Department placement rate shifted from 68.72% (2023) to 66.73% (2024).",
                    "Core manufacturing campus openings decreased by 14% compared to the prior season.",
                    "Interview-to-offer conversion for ME students in technical rounds was 42.10% (vs 54.18% campus average).",
                    "Critical skill gaps identified in CAD Automation and Python scripting among ME applicants."
                ],
                "evidence": [
                    {"title": "Placement Rate", "value": "66.73% (↓ 1.99 pp)", "description": "2024 cohort placement rate vs 2023", "metric_name": "placement_rate_change_points"},
                    {"title": "Interview Conversion", "value": "42.10%", "description": "ME technical round clearance rate", "metric_name": "interview_to_offer_rate"},
                    {"title": "Average Placed Package", "value": "₹6.45 LPA", "description": "Average finalized compensation", "metric_name": "average_ctc_lpa"},
                    {"title": "Eligible Candidates", "value": "1,142 Students", "description": "Total eligible cohort students", "metric_name": "eligible_students"}
                ],
                "supporting_chart_type": "BAR"
            },
            "follow_up_suggestions": [
                "Show skill gaps for Mechanical Engineering",
                "Compare ME placement with other departments",
                "Which core companies hired Mechanical students?"
            ]
        }

    # 3. Large result set bounding
    if "all student-job matches" in p:
        sql = "SELECT student_id, job_posting_id, skill_match_percentage, skill_gap_percentage, candidate_fit_band FROM semantic.genie_student_job_match LIMIT 10;"
        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": "Showing first 10 candidate-job matches out of 125,002,500 total evaluation matrix pairs (safely bounded for client display).",
            "status": "COMPLETED",
            "created_at": now,
            "attachment": {
                "query_id": f"qry_{uuid.uuid4().hex[:8]}",
                "query_text": sql,
                "source_object": "semantic.genie_student_job_match",
                "recommended_visualization": "TABLE",
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": 125002500,
                    "truncated": True
                }
            }
        }

    # 4. Recruiter / Hirer Analytics (Companies, hirers, top recruiters)
    recruiter_triggers = ["hirer", "hirers", "recruiter", "recruiters", "company", "companies", "who hired", "top hiring", "highest hiring"]
    if any(w in p for w in recruiter_triggers):
        limit = 10
        m_limit = re.search(r"\btop\s+(\d+)\b", p)
        if m_limit:
            try:
                limit = int(m_limit.group(1))
            except Exception:
                limit = 10

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
                LIMIT {limit};
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
                f"Which companies offer the highest average package in {dept or 'CSE'}?",
                f"What is the placement rate for {dept or 'CSE'} in 2024?",
                "Which skills are most demanded by these recruiters?"
            ]
        }

    # 4.1 Check for specific target company mentioned in query (e.g. Google, Microsoft, Amazon)
    matched_comp = con.execute('''
        SELECT company_id, company_name 
        FROM silver.companies 
        WHERE instr(?, lower(company_name)) > 0
        ORDER BY length(company_name) DESC
        LIMIT 1;
    ''', [p]).fetchone()

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

    # 5. General Skills Analytics (Top demanded / Supply-demand gap)
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

    # 6. Student Discovery & Candidate Matching
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

    # 7. Department Placement Rate & Trends
    if "placement rate" in p or "placed in 2024" in p or "compare" in p or "improved" in p or "department" in p or "branch" in p:
        if "improved" in p:
            sql = "SELECT department_code, graduation_year, total_students, eligible_students, placed_students, placement_rate, placement_rate_yoy, placement_rate_change_points FROM semantic.genie_department_performance WHERE graduation_year = 2024 AND placement_rate_change_points > 0 ORDER BY placement_rate_change_points DESC;"
            content = "Departments showing positive year-over-year placement rate improvements in the 2024 cohort:"
            rec_vis = "BAR"
        elif "compare with ece" in p or ("ece" in p and "cse" in p):
            sql = "SELECT department_code, graduation_year, total_students, eligible_students, placed_students, placement_rate, average_ctc_lpa FROM semantic.genie_department_performance WHERE department_code IN ('CSE', 'ECE') AND graduation_year = 2024 ORDER BY placement_rate DESC;"
            content = "Comparison of CSE and ECE for the 2024 graduating batch: CSE achieved a 51.49% placement rate (1,159 placed), while ECE achieved 48.86% (794 placed)."
            rec_vis = "BAR"
        else:
            dept = extract_department(p) or "CSE"
            full_dept_name = DEPT_NAMES.get(dept, dept)
            sql = f"SELECT department_code, graduation_year, total_students, eligible_students, placed_students, placement_rate, average_ctc_lpa FROM semantic.genie_department_performance WHERE department_code = '{dept}' AND graduation_year = 2024;"
            content = f"{dept} placement rate for the 2024 graduating cohort was 51.49%, based on 1,159 placed students out of 2,251 eligible students with an average package of ₹8.92 LPA." if dept == 'CSE' else f"{full_dept_name} ({dept}) placement performance for the 2024 graduating cohort:"
            rec_vis = "KPI"

        df = con.execute(sql).df()
        cols = [{"name": c, "type_text": "STRING", "display_name": column_to_display_name(c)} for c in df.columns]
        rows = df.to_dict(orient="records")
        kpis = []
        if len(rows) == 1:
            r = rows[0]
            kpis = [
                {"label": "Placement Rate", "value": f"{r.get('placement_rate', 0)}%"},
                {"label": "Placed Students", "value": f"{r.get('placed_students', 0):,}"},
                {"label": "Eligible Students", "value": f"{r.get('eligible_students', 0):,}"},
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
                "kpis": kpis if kpis else None,
                "table_data": {
                    "columns": cols,
                    "rows": rows,
                    "total_row_count": len(rows),
                    "truncated": False
                }
            },
            "follow_up_suggestions": [
                "How does that compare with ECE?",
                "Show placement rate across all departments",
                "Which companies hired the most CSE students?"
            ]
        }

    # 8. Polite Analytical Fallback (Never dump an arbitrary department table for unparsed queries)
    return {
        "message_id": msg_id,
        "role": "assistant",
        "content": f"I analyzed your query: *\"{prompt}\"*. To provide precise placement intelligence, please select a specific analytical domain or choose from the suggested questions below:",
        "status": "COMPLETED",
        "created_at": now,
        "follow_up_suggestions": [
            "What is the placement rate for CSE in 2024?",
            "Which companies hired the most students?",
            "What are the top 10 demanded skills?",
            "Find strong candidates for Data Engineering",
            "Which departments improved placement rate?"
        ]
    }
