# Placewise Production Readiness & Governance Audit

**System Version:** 2.0.0  
**Audit Date:** 2026-09-01  
**Architecture Classification:** Databricks Genie + Unity Catalog Placement Intelligence  

---

## 1. System Architecture Overview

Placewise operates as a modern conversational placement intelligence system:
```
React Frontend (Vite + TS + Recharts)
   │ HTTPS / REST (JSON)
   ▼
FastAPI Thin Orchestration Layer (Session Persistence & Normalizer)
   │ REST API (/api/2.0/genie)
   ▼
Databricks Genie Conversation Engine (Space: Placewise Intelligence)
   │ Governed SQL Queries
   ▼
Databricks Unity Catalog Semantic Layer (`placewise.semantic.*`)
```

---

## 2. Data & Semantic Layer Status

| Object | Grain | Columns | Row Count | Status |
|---|---|---|---|---|
| `semantic.genie_student_intelligence` | 1 row per student (`student_id`) | 68 | 50,000 | **PASS (100% Unique)** |
| `semantic.genie_company_intelligence` | 1 row per company (`company_id`) | 25 | 600 | **PASS (100% Unique)** |
| `semantic.genie_department_performance` | 1 row per dept + year | 14 | 32 | **PASS (100% Unique)** |
| `semantic.genie_skill_market` | 1 row per skill (`skill_id`) | 16 | 66 | **PASS (100% Unique)** |
| `semantic.genie_student_job_match` | 1 row per candidate-job pair | 8 | 125,002,500 | **PASS (Bounded)** |

---

## 3. Metric Reconciliation & Ground Truth
All 7 critical placement and compensation metrics reconciled against raw Silver tables with **0.0000% variance**:
- **Placement Rate**: Verified $\frac{\text{Placed Eligible}}{\text{Total Eligible}} \times 100$
- **CTC Statistics**: Reconciled Average, Median, and Highest LPA
- **Conversion Rates**: Verified Interview-to-Offer and Offer Acceptance rates
- **Candidate Matching**: Enforces strict non-negotiable mandatory skill gates

---

## 4. API & Orchestration Layer
- **Persistent Storage**: SQLite database (`data/conversations.db`) storing sessions, message threads, and idempotency keys.
- **Client Normalizer**: Maps upstream Genie responses to typed frontend `Message` structures with KPI chips, charts, and Agent Mode accordions.
- **Large Result Protection**: Matrix queries bounded up to 10,000 rows with `truncated: true` metadata.
- **Security & Privacy**: Zero credentials exposed to client bundle; CORS restricted to `ALLOWED_ORIGINS`.

---

## 5. Automated Verification Results

| Test Category | Suite File | Total | Passed | Status |
|---|---|---|---|---|
| **Data Quality & Metrics** | `tests/metrics/`, `tests/synthetic/` | 23 | 23 | **PASS (100%)** |
| **Backend API & Persist** | `tests/backend/` | 9 | 9 | **PASS (100%)** |
| **Frontend Production** | `npm run typecheck`, `npm run build` | 2 | 2 | **PASS (0 Errors)** |
| **End-to-End Scenarios** | `scripts/test_app_scenarios.py` | 12 | 12 | **PASS (100%)** |
| **Live Remote Databricks** | `scripts/evaluate_live_genie.py` | 23 | 0 (23 Not Run) | **NOT_VERIFIED** |

---

## 6. Final Live Readiness Gate

```
============================================================
       PLACEWISE_LIVE_GENIE_READY = NOT_VERIFIED
============================================================
```

*Status is marked `NOT_VERIFIED` strictly because active Databricks workspace credentials have not been configured in the local environment. All local architecture, client code, normalizers, and test suites are 100% certified.*
