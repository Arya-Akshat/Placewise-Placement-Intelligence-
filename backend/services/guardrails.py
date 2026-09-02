"""
PLACEWISE — Guardrails & Query Safety Engine
============================================
Provides content moderation, domain boundaries, and graceful fallback
for inappropriate, abusive, or off-topic queries.
"""

import re
from typing import Optional, Tuple, Dict, Any, List

# 1. Blocked Inappropriate / Explicit / Abusive terms (Regex patterns)
PROFANITY_PATTERNS = [
    r"\b(fuck|shit|bitch|asshole|bastard|dick|pussy|cock|cunt|slut|whore|boobs|nude|sex|porn|f\*ck|s\*it)\b",
    r"\b(how to (have sex|fuck|kiss|date|hookup|seduce))\b",
    r"\b(kill|murder|suicide|attack|bomb|terrorist|hack)\b",
    r"\b(hate|racist|slur)\b"
]

# 2. Placement Domain Keywords
PLACEMENT_DOMAIN_KEYWORDS = [
    "placement", "placed", "place", "unplaced", "eligible", "offer", "offers",
    "ctc", "lpa", "package", "salary", "compensation", "highest", "lowest", "average", "median",
    "department", "dept", "branch", "cse", "ece", "mech", "mechanical", "civil", "ee", "electrical", "aiml", "it", "btech", "mtech",
    "company", "companies", "recruiter", "recruiters", "hiring", "hire", "hired", "hirer", "hirers", "interview", "interviews", "shortlist",
    "skill", "skills", "technology", "technologies", "python", "sql", "java", "react", "cloud", "aws", "docker", "supply", "demand", "gap",
    "student", "students", "candidate", "candidates", "cgpa", "readiness", "score", "grade", "backlog", "funnel",
    "batch", "year", "2021", "2022", "2023", "2024", "trend", "trends", "compare", "performance", "improve", "decline",
    "selectivity", "conversion", "acceptance", "shortlisted", "rate", "percentage", "ratio",
    "college", "campus", "institution", "rvce", "university", "model"
]

GREETING_PATTERNS = [
    r"^(hi|hello|hey|greetings|good\s*(morning|afternoon|evening)|howdy)\b",
    r"^(who are you|what can you do|help|what is placewise|what is this|what model|which model)\b"
]

class GuardrailResult:
    def __init__(self, is_allowed: bool, category: str, response_text: Optional[str] = None, suggestions: Optional[List[str]] = None):
        self.is_allowed = is_allowed
        self.category = category  # 'SAFE', 'INAPPROPRIATE', 'GREETING', 'OUT_OF_DOMAIN'
        self.response_text = response_text
        self.suggestions = suggestions or [
            "What is the placement rate for CSE in 2024?",
            "Which companies hired the most students?",
            "What are the top 10 demanded skills?",
            "Show high-readiness students without offers."
        ]

def check_guardrails(prompt: str) -> GuardrailResult:
    p = prompt.strip().lower()

    # 1. Inappropriate / Profanity Check
    for pattern in PROFANITY_PATTERNS:
        if re.search(pattern, p, re.IGNORECASE):
            return GuardrailResult(
                is_allowed=False,
                category="INAPPROPRIATE",
                response_text=(
                    "I am Placewise, an institutional placement intelligence assistant. "
                    "I can only process professional queries regarding campus placements, student readiness, "
                    "recruiting companies, and department analytics. Please keep your questions respectful and placement-related."
                ),
                suggestions=[
                    "What is the placement rate for CSE in 2024?",
                    "Which companies hired the most students?",
                    "What are the top demanded skills?"
                ]
            )

    # 2. System Architecture / Model Inquiry Check
    if any(m in p for m in ["what model", "which model", "model are you", "model are u", "tech stack", "what llm"]):
        return GuardrailResult(
            is_allowed=False,
            category="SYSTEM_INFO",
            response_text=(
                "**Placewise AI Architecture & Model Stack:**\n\n"
                "• **AI Engine**: Databricks Genie Agent using specialized text-to-SQL foundation models\n"
                "• **Governed Data Layer**: Databricks Unity Catalog (`placewise.semantic.*`)\n"
                "• **Orchestration Layer**: FastAPI backend with SQLite conversation persistence\n"
                "• **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS with dark/light themes\n"
                "• **Grounded Data**: Department benchmarks, corporate recruiter compensation, and student-job candidate matching"
            ),
            suggestions=[
                "What is the placement rate for CSE in 2024?",
                "Which companies hired the most students?",
                "What are the top 10 demanded skills?",
                "Find strong candidates for Data Engineering"
            ]
        )

    # 3. Greeting / Identity Check
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, p, re.IGNORECASE):
            return GuardrailResult(
                is_allowed=False,
                category="GREETING",
                response_text=(
                    "Hello! I am **Placewise**, your campus placement intelligence assistant. "
                    "I am connected to the governed institutional semantic layer to help you analyze:\n\n"
                    "• **Department Performance**: Placement rates, batch YoY trends, and salary distributions\n"
                    "• **Corporate Recruiting**: Top hiring companies, average CTC packages, and conversion rates\n"
                    "• **Skill Market Dynamics**: Most demanded technical skills and student supply gaps\n"
                    "• **Candidate Matching**: High-readiness students and role suitability\n\n"
                    "How can I assist your placement cell or analytical query today?"
                ),
                suggestions=[
                    "What is the placement rate for CSE in 2024?",
                    "Which companies hired the most students?",
                    "Which skills have high demand but low student supply?",
                    "Find strong candidates for Data Engineering."
                ]
            )

    # 3. Domain Relevance Check
    # If the query is very short or completely lacks any placement domain concept:
    words = re.findall(r"\b[a-z0-9_]+\b", p)
    has_domain_word = any(w in PLACEMENT_DOMAIN_KEYWORDS for w in words)

    # Allow common comparative pronouns if part of follow-up (e.g. "what about ece", "how does that compare")
    is_follow_up = any(phrase in p for phrase in ["how does that", "what about", "compare that", "show more", "and for"])

    if not has_domain_word and not is_follow_up:
        return GuardrailResult(
            is_allowed=False,
            category="OUT_OF_DOMAIN",
            response_text=(
                f"I couldn't identify a placement or institutional hiring topic in your question: *\"{prompt}\"*.\n\n"
                "I am specialized in campus placement analytics, student readiness scoring, recruiter intelligence, "
                "and departmental benchmarks. Here are some questions you can ask me:"
            ),
            suggestions=[
                "What is the placement rate by department in 2024?",
                "Which companies offered the highest packages?",
                "What skills are most demanded by recruiters?",
                "Find the strongest candidates for Data Engineering."
            ]
        )

    return GuardrailResult(is_allowed=True, category="SAFE")
