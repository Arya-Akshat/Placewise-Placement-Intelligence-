"""
PLACEWISE -- Authoritative Entity & Intent Extraction Engine
==========================================================
Deterministic, multi-pattern NLP extractor for entities (companies,
departments, roles, skills, metrics, thresholds, years) grounded in
the Placewise analytical database schema.

Design Principles:
  1. Longest-match-first: All synonym lists are sorted by string length
     descending so "electrical and electronics" matches EEE before
     "electronics" matches ECE.
  2. Word-boundary matching: Prevents partial substring hallucinations.
  3. Pronoun-safe: Short ambiguous words ("me", "it", "ce") have
     context-aware guards to prevent false triggers.
"""

import re, duckdb, os
from typing import Dict, Any, List, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/placewise.duckdb")

DEPARTMENT_SYNONYMS = {
    "CSE": [
        "computer science and engineering", "computer science & engineering",
        "computer science", "comp sci", "cse", "cs branch", "cs dept",
        "computer branch", "computer engineering", "cs department"
    ],
    "ECE": [
        "electronics and communication engineering", "electronics and communication",
        "electronics & communication engineering", "electronics & communication",
        "electronics engineering", "electronics", "ece", "ec branch", "ec dept", "enc"
    ],
    "IT": [
        "information technology", "info tech",
        "it branch", "it dept", "it department",
        "it students", "it placement", "it placements"
    ],
    "AIML": [
        "artificial intelligence & machine learning", "artificial intelligence and machine learning",
        "artificial intelligence", "ai & ml", "ai and ml", "aiml", "ai branch", "ml branch",
        "machine learning branch", "data science branch", "data science department"
    ],
    "ME": [
        "mechanical engineering", "mechanical", "mech",
        "me branch", "me dept", "me department"
    ],
    "CE": [
        "civil engineering", "civil",
        "ce branch", "ce dept", "ce department"
    ],
    "EEE": [
        "electrical and electronics engineering", "electrical and electronics",
        "electrical & electronics engineering", "electrical & electronics",
        "electrical engineering", "electrical", "eee", "ee branch", "ee dept"
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
        "data analyst", "business analyst", "bi analyst", "data analytics"
    ],
    "machine_learning": [
        "machine learning engineer", "ml engineer", "ai engineer", "data scientist",
        "deep learning engineer", "machine learning", "deep learning"
    ],
    "software_engineering": [
        "software engineering", "software engineer", "software developer", "sde", "swe",
        "software development", "programmer"
    ],
    "devops": [
        "devops engineer", "site reliability", "sre", "devops", "cloud engineer"
    ],
    "product_management": [
        "product manager", "product management", "apm", "associate product manager"
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
    "qualcomm": ["qualcomm"],
    "uber": ["uber"],
    "meta": ["meta", "facebook"],
    "apple": ["apple"],
    "ibm": ["ibm"],
    "deloitte": ["deloitte"],
    "accenture": ["accenture"],
    "cognizant": ["cognizant"],
    "capgemini": ["capgemini"],
    "samsung": ["samsung"],
    "intel": ["intel"],
    "vmware": ["vmware"],
    "salesforce": ["salesforce"],
    "jpmorgan": ["jpmorgan", "jp morgan", "jpmc", "chase"],
    "morgan stanley": ["morgan stanley"],
    "deutsche bank": ["deutsche bank", "deutsche"],
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
    # Standalone "IT" check with context guard
    # Only match standalone "IT" if it's clearly referring to a department
    if re.search(r"\bit\b", t):
        it_context_words = [
            "student", "students", "placement", "placements", "placed",
            "department", "dept", "branch", "rate", "package", "salary",
            "hirer", "hirers", "recruiter", "company", "companies",
            "average", "highest", "cgpa", "batch", "2024", "2023"
        ]
        if any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in it_context_words):
            return "IT"
    return None

def extract_all_departments(text: str) -> List[str]:
    t = f" {text.lower()} "
    found = []
    matched_ranges = []
    for syn, dept_code in _SORTED_DEPT_PATTERNS:
        for m in re.finditer(r"\b" + re.escape(syn) + r"\b", t):
            s, e = m.span()
            if not any(ms <= s and e <= me for ms, me in matched_ranges):
                matched_ranges.append((s, e))
                if dept_code not in found:
                    found.append(dept_code)
    # Same standalone IT context check
    if "IT" not in found and re.search(r"\bit\b", t):
        it_context_words = [
            "student", "students", "placement", "placements", "placed",
            "department", "dept", "branch", "rate", "package", "salary",
            "hirer", "hirers", "recruiter", "company", "companies",
            "average", "highest", "cgpa", "batch", "2024", "2023",
            "compare", "vs", "cse", "ece", "me", "eee"
        ]
        if any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in it_context_words):
            found.append("IT")
    return found

def extract_company(text: str) -> Optional[Tuple[str, str]]:
    t = f" {text.lower()} "
    comps, _ = get_master_data()

    # 1. Check known aliases first (handles abbreviations and parent companies)
    for alias_target, alias_list in COMPANY_ALIASES.items():
        for al in alias_list:
            if re.search(r"\b" + re.escape(al) + r"\b", t):
                for cid, cname in comps:
                    if alias_target in cname.lower():
                        return cid, cname

    # 2. Check full company list (longest name first to avoid substring matches)
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


# --- Intent Classification ---

INTENT_KEYWORDS = {
    "company_info": [
        "tell me about", "about", "info", "information", "details",
        "stats", "statistics", "profile", "overview", "doing", "performance"
    ],
    "placement_count": [
        "how many", "count", "number", "total", "placed", "hired",
        "recruit", "recruited", "placements", "hires"
    ],
    "package_inquiry": [
        "package", "packages", "ctc", "salary", "salaries", "pay",
        "paying", "compensation", "offer", "offered", "lpa", "lakh",
        "how much"
    ],
    "skill_inquiry": [
        "skill", "skills", "interview", "prepare", "preparation",
        "clear", "learn", "crack", "criteria", "requirements",
        "required", "needed", "get placed", "how to get into"
    ],
    "comparison": [
        "compare", "comparison", "vs", "versus", "between",
        "difference", "better", "worse"
    ],
    "ranking": [
        "best", "worst", "top", "bottom", "highest", "lowest",
        "maximum", "minimum", "most", "least", "rank", "ranking"
    ],
    "department_overview": [
        "department", "departments", "branch", "branches",
        "all departments", "every department", "each department",
        "across departments", "by department", "department wise"
    ],
    "trend": [
        "improved", "improvement", "declined", "trend", "trends",
        "growth", "change", "year over year", "yoy"
    ]
}


def classify_intents(text: str) -> List[str]:
    """Return list of detected intent categories from the query text."""
    t = f" {text.lower()} "
    detected = []
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", t):
                if intent not in detected:
                    detected.append(intent)
                break
    return detected


def extract_numeric_thresholds(text: str) -> Dict[str, Any]:
    t = text.lower()
    res = {}

    # Top N limit (e.g. top 5, top 10)
    m_top = re.search(r"\btop\s+(\d+)\b", t)
    if m_top:
        res["limit"] = int(m_top.group(1))

    # Package / CTC threshold (e.g. > 20 LPA, more than 15 lakh, above 12)
    m_lpa = re.search(r"(?:more than|greater than|above|over|exceeding|>|>=)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh)?", t)
    if m_lpa and any(w in t for w in ["package", "ctc", "salary", "paying", "offer", "lpa", "lakh", "pay"]):
        res["min_ctc_lpa"] = float(m_lpa.group(1))

    # Less-than threshold (e.g. below 5 LPA, less than 10 LPA)
    m_lpa_lt = re.search(r"(?:less than|below|under|<|<=)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh)?", t)
    if m_lpa_lt and any(w in t for w in ["package", "ctc", "salary", "paying", "offer", "lpa", "lakh", "pay"]):
        res["max_ctc_lpa"] = float(m_lpa_lt.group(1))

    # CGPA threshold
    m_cgpa = re.search(r"cgpa\s*(?:of|is|equals|==|=|greater than|above|over|>|>=)?\s*(\d+(?:\.\d+)?)", t)
    if not m_cgpa:
        m_cgpa = re.search(r"(?:greater than|above|over|>|>=|of|is)\s*(\d+(?:\.\d+)?)\s*cgpa", t)
    if m_cgpa:
        res["min_cgpa"] = float(m_cgpa.group(1))

    # Company Type (PRODUCT, SERVICES, STARTUP, CONSULTING)
    if re.search(r"\bproduct\b", t):
        res["company_type"] = "PRODUCT"
    elif re.search(r"\bservice\b", t) or re.search(r"\bservices\b", t):
        res["company_type"] = "SERVICES"
    elif re.search(r"\bstartup\b", t) or re.search(r"\bstartups\b", t):
        res["company_type"] = "STARTUP"
    elif re.search(r"\bconsulting\b", t):
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
    intents = classify_intents(p)

    return {
        "raw_query": query,
        "clean_query": p,
        "department": dept,
        "all_departments": all_depts,
        "company": comp,
        "role": role,
        "skills": skills,
        "thresholds": thresholds,
        "intents": intents
    }
