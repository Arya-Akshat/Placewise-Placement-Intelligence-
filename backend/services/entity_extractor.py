"""
PLACEWISE — Authoritative Entity & Intent Extraction Engine
==========================================================
Deterministic, multi-pattern NLP extractor for entities (companies,
departments, roles, skills, metrics, thresholds, years) grounded in
the Placewise analytical database schema.
"""

import re, duckdb, os
from typing import Dict, Any, List, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/placewise.duckdb")

DEPARTMENT_SYNONYMS = {
    "CSE": [
        "computer science and engineering", "computer science & engineering",
        "computer science", "comp sci", "cse", "cs branch", "cs dept", "computer branch"
    ],
    "ECE": [
        "electronics and communication engineering", "electronics and communication",
        "electronics & communication", "electronics", "ece", "ec branch", "ec dept", "enc"
    ],
    "IT": [
        "information technology", "info tech", "it branch", "it dept", "it department"
    ],
    "AIML": [
        "artificial intelligence & machine learning", "artificial intelligence and machine learning",
        "artificial intelligence", "ai & ml", "ai and ml", "aiml", "ai branch", "ml branch",
        "machine learning branch", "data science"
    ],
    "ME": [
        "mechanical engineering", "mechanical", "mech", "me branch", "me dept", "me department"
    ],
    "CE": [
        "civil engineering", "civil", "ce branch", "ce dept", "ce department"
    ],
    "EEE": [
        "electrical and electronics engineering", "electrical and electronics",
        "electrical & electronics", "electrical engineering", "electrical", "eee", "ee branch", "ee dept"
    ],
    "CH": [
        "chemical engineering", "chemical", "chem", "ch branch", "ch dept"
    ]
}

# Precompile flattened department patterns sorted by length descending (longest match wins)
_SORTED_DEPT_PATTERNS = []
for _dcode, _syns in DEPARTMENT_SYNONYMS.items():
    for _s in _syns:
        _SORTED_DEPT_PATTERNS.append((_s, _dcode))
_SORTED_DEPT_PATTERNS.sort(key=lambda x: len(x[0]), reverse=True)

DEPT_DISPLAY_NAMES = {
    "CSE": "Computer Science & Engineering",
    "ECE": "Electronics & Communication Engineering",
    "IT": "Information Technology",
    "AIML": "Artificial Intelligence & ML",
    "ME": "Mechanical Engineering",
    "CE": "Civil Engineering",
    "EEE": "Electrical & Electronics Engineering",
    "CH": "Chemical Engineering"
}

ROLE_SYNONYMS = {
    "frontend": [
        "frontend developer", "front end developer", "react developer", "ui developer",
        "web developer", "frontend", "front end"
    ],
    "backend": [
        "backend developer", "back end developer", "api developer", "backend", "back end"
    ],
    "data_engineering": [
        "data engineering", "data engineer", "big data engineer", "etl engineer", "data pipeline"
    ],
    "data_analyst": [
        "data analyst", "business analyst", "bi analyst", "analyst", "analytics", "data analytics"
    ],
    "machine_learning": [
        "machine learning", "ml engineer", "ai engineer", "data scientist", "deep learning", "nlp"
    ],
    "software_engineering": [
        "software engineering", "software engineer", "software developer", "sde", "swe",
        "developer", "software development", "programmer"
    ]
}

# Precompile flattened role patterns sorted by length descending
_SORTED_ROLE_PATTERNS = []
for _rk, _syns in ROLE_SYNONYMS.items():
    for _s in _syns:
        _SORTED_ROLE_PATTERNS.append((_s, _rk))
_SORTED_ROLE_PATTERNS.sort(key=lambda x: len(x[0]), reverse=True)

COMPANY_ALIASES = {
    "google": ["google", "alphabet", "goog"],
    "microsoft": ["microsoft", "msft"],
    "amazon": ["amazon", "aws", "amzn"],
    "nvidia": ["nvidia", "nvda"],
    "tcs": ["tcs", "tata consultancy", "tata consultancy services"],
    "infosys": ["infosys", "infy"],
    "wipro": ["wipro"],
    "cred": ["cred"],
    "adobe": ["adobe"],
    "thoughtworks": ["thoughtworks"],
    "goldman sachs": ["goldman sachs", "goldman", "gs"],
    "flipkart": ["flipkart"],
    "walmart": ["walmart", "walmart global tech"],
    "oracle": ["oracle"],
    "cisco": ["cisco"],
    "qualcomm": ["qualcomm"]
}

_COMPANY_CACHE = None
_SKILLS_CACHE = None

def get_master_data():
    global _COMPANY_CACHE, _SKILLS_CACHE
    if _COMPANY_CACHE is None or _SKILLS_CACHE is None:
        con = duckdb.connect(DB_PATH, read_only=True)
        comps = con.execute("SELECT company_id, company_name FROM silver.companies;").fetchall()
        _COMPANY_CACHE = sorted(comps, key=lambda x: len(x[1]), reverse=True)
        sk = con.execute("SELECT skill_id, skill_name, skill_category FROM silver.skills;").fetchall()
        _SKILLS_CACHE = sorted(sk, key=lambda x: len(x[1]), reverse=True)
        con.close()
    return _COMPANY_CACHE, _SKILLS_CACHE

def extract_department(text: str) -> Optional[str]:
    t = f" {text.lower()} "
    for syn, dept_code in _SORTED_DEPT_PATTERNS:
        if re.search(r"\b" + re.escape(syn) + r"\b", t):
            return dept_code
    return None

def extract_all_departments(text: str) -> List[str]:
    t = f" {text.lower()} "
    found = []
    # Track positions of matches to avoid sub-match duplication
    matched_ranges = []
    for syn, dept_code in _SORTED_DEPT_PATTERNS:
        for m in re.finditer(r"\b" + re.escape(syn) + r"\b", t):
            s, e = m.span()
            if not any(ms <= s and e <= me for ms, me in matched_ranges):
                matched_ranges.append((s, e))
                if dept_code not in found:
                    found.append(dept_code)
    return found

def extract_company(text: str) -> Optional[Tuple[str, str]]:
    t = f" {text.lower()} "
    comps, _ = get_master_data()

    # 1. Check known aliases first
    for alias_target, alias_list in COMPANY_ALIASES.items():
        for al in alias_list:
            if re.search(r"\b" + re.escape(al) + r"\b", t):
                for cid, cname in comps:
                    if alias_target in cname.lower():
                        return cid, cname

    # 2. Check full company list
    for cid, cname in comps:
        cn = cname.lower()
        if len(cn) >= 3 and re.search(r"\b" + re.escape(cn) + r"\b", t):
            return cid, cname
    return None

def extract_role(text: str) -> Optional[str]:
    t = f" {text.lower()} "
    for syn, role_key in _SORTED_ROLE_PATTERNS:
        if re.search(r"\b" + re.escape(syn) + r"\b", t):
            return role_key
    return None

def extract_skills(text: str) -> List[Tuple[str, str, str]]:
    t = text.lower()
    _, skills = get_master_data()
    matched = []
    for sid, sname, scat in skills:
        sn = sname.lower()
        if sn in ["c++", "c"]:
            if re.search(r"\bc\+\+\b", t):
                matched.append((sid, sname, scat))
        elif len(sn) >= 3 and re.search(r"\b" + re.escape(sn) + r"\b", t):
            matched.append((sid, sname, scat))
    return matched

def extract_numeric_thresholds(text: str) -> Dict[str, Any]:
    t = text.lower()
    res = {}
    
    # Top N limit (e.g. top 5, top 10)
    m_top = re.search(r"\btop\s+(\d+)\b", t)
    if m_top:
        res["limit"] = int(m_top.group(1))

    # Package / CTC threshold (e.g. > 20 LPA, more than 15 lakh, above 12)
    m_lpa = re.search(r"(?:more than|greater than|above|>|>=)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh)?", t)
    if m_lpa and any(w in t for w in ["package", "ctc", "salary", "paying", "offer", "lpa", "lakh"]):
        res["min_ctc_lpa"] = float(m_lpa.group(1))

    # CGPA threshold (e.g. CGPA > 8.5, above 9 cgpa)
    m_cgpa = re.search(r"cgpa\s*(?:greater than|>|above|>=)?\s*(\d+(?:\.\d+)?)", t)
    if not m_cgpa:
        m_cgpa = re.search(r"(?:greater than|>|above|>=)\s*(\d+(?:\.\d+)?)\s*cgpa", t)
    if m_cgpa:
        res["min_cgpa"] = float(m_cgpa.group(1))

    # Company Type (PRODUCT, SERVICES, STARTUP, CONSULTING)
    if "product" in t:
        res["company_type"] = "PRODUCT"
    elif "service" in t:
        res["company_type"] = "SERVICES"
    elif "startup" in t:
        res["company_type"] = "STARTUP"
    elif "consulting" in t:
        res["company_type"] = "CONSULTING"

    # Year (e.g. 2024, 2023, 2022)
    m_yr = re.search(r"\b(201\d|202\d)\b", t)
    if m_yr:
        res["year"] = int(m_yr.group(1))
    else:
        res["year"] = 2024

    return res

def parse_query_semantics(query: str) -> Dict[str, Any]:
    p = query.strip().lower()
    dept = extract_department(p)
    all_depts = extract_all_departments(p)
    comp = extract_company(p)
    role = extract_role(p)
    skills = extract_skills(p)
    thresholds = extract_numeric_thresholds(p)

    return {
        "raw_query": query,
        "clean_query": p,
        "department": dept,
        "all_departments": all_depts,
        "company": comp,
        "role": role,
        "skills": skills,
        "thresholds": thresholds
    }
