# Placewise Backend Architecture & Databricks Genie Integration

**Architecture Pattern:** Thin Application Orchestration Layer  
**Framework:** FastAPI (Python 3.10+)  
**Data Engine:** Databricks Genie Agent + Unity Catalog (`placewise.semantic`)  
**State Persistence:** SQLite Database (`data/conversations.db`)  
**Authentication:** Extensible OAuth / JWT Service Principal Hook (`get_current_user`)  

---

## 1. System Data Flow

```
┌────────────────────────────────────────────────────────┐
│               Placewise React Frontend                 │
│                 (Vite + Tailwind CSS)                  │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS / REST (JSON)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Placewise FastAPI Backend                  │
│       - Session & Idempotency Management (SQLite)      │
│       - DatabricksGenieClient (OAuth Token Auth)       │
│       - Safe Response Normalization & Result Bounding  │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (/api/2.0/genie)
                            ▼
┌────────────────────────────────────────────────────────┐
│            Databricks Genie Conversation API           │
│         (Space: Placewise Placement Intelligence)      │
└───────────────────────────┬────────────────────────────┘
                            │ Governed SQL Queries
                            ▼
┌────────────────────────────────────────────────────────┐
│         Databricks Unity Catalog Semantic Layer        │
│  (genie_student, genie_company, genie_department, ...) │
└────────────────────────────────────────────────────────┘
```

---

## 2. Core Service Modules

1. **`backend/services/databricks_genie.py` (`DatabricksGenieClient`)**:
   - Manages asynchronous conversation lifecycles via `/api/2.0/genie/spaces/{space_id}/start-conversation` and `/api/2.0/genie/spaces/{space_id}/conversations/{id}/messages`.
   - Implements exponential backoff polling with jitter up to configurable timeouts (`GENIE_TIMEOUT_SECONDS = 30`, `GENIE_AGENT_TIMEOUT_SECONDS = 90`).
   - Fetches tabular query manifests and data arrays from `/query-result`.
   - Normalizes raw Genie responses into the Placewise `Message` schema with display name mappings, KPI extractions, and chart recommendation inferences.
   - Enforces large-result bounding (up to `GENIE_MAX_RESULT_ROWS = 10000`, flagged with `truncated: true`).

2. **`backend/db/database.py` (SQLite Persistence)**:
   - Persists session metadata in `conversations`, `messages`, and `idempotency_records` tables.
   - Preserves complete conversational history across reloads.
   - Prevents duplicate query submission via `client_request_id` lookup.

3. **`backend/main.py` (FastAPI Router)**:
   - Provides `/api/v1/conversations`, `/api/v1/conversations/{id}/messages`, `/api/v1/health`, and `/api/v1/health/ready`.
   - Restricts CORS to `ALLOWED_ORIGINS` (default `http://localhost:3000`).
   - Provides per-session `asyncio.Lock` to prevent concurrent conflicting requests.
   - Maps errors into standard HTTP error responses (`401`, `403`, `404`, `429`, `503`, `504`).
