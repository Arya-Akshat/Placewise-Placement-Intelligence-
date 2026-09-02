# Placewise — Campus Placement Intelligence Platform

Placewise is an institutional analytics and decision-support platform designed for university placement cells, academic department heads, and campus recruiters. It centralizes student academic records, recruitment drive telemetry, skill assessments, and company hiring trends into a governed data platform powered by Databricks Unity Catalog and a conversational natural-language analytics interface.

---

## System Architecture

The platform uses a layered Medallion architecture for data governance, with an operational FastAPI orchestration service and a React-based analytics dashboard.

```
┌───────────────────────────────────────────────────────────┐
│                     React 18 Frontend                     │
│  - Executive Analytics Dashboard (KPIs, Trends, Heatmaps) │
│  - Conversational Query Interface (Light / Dark Theme)     │
└─────────────────────────────┬─────────────────────────────┘
                              │ HTTP / REST
┌─────────────────────────────▼─────────────────────────────┐
│                    FastAPI Backend Router                 │
│  - Session Management & Idempotency Store (SQLite)        │
│  - Intent Classifier & Domain Guardrails                  │
│  - Databricks Genie Client with Governed DuckDB Fallback  │
└─────────────────────────────┬─────────────────────────────┘
                              │
       ┌──────────────────────┴──────────────────────┐
       ▼                                             ▼
┌──────────────────────────────┐       ┌──────────────────────────────┐
│   Databricks Unity Catalog   │       │   Local Analytics Mirror     │
│   - placewise.bronze         │       │   - Embedded DuckDB Engine   │
│   - placewise.silver         │       │   - In-memory OLAP           │
│   - placewise.gold           │       │   - Complete semantic parity │
│   - placewise.semantic       │       └──────────────────────────────┘
└──────────────────────────────┘
```

---

## Core Capabilities

1. **Department Placement Performance & Benchmarking**
   - Department-level tracking of eligible vs. placed student counts, placement conversion rates, and year-over-year trajectory (percentage points change).
   - Comparative analysis across engineering disciplines (e.g., CSE, ECE, Mechanical, Civil, AIML).

2. **Corporate Recruiter & Compensation Intelligence**
   - Detailed employer hiring profiles, including recruitment volume, average and highest compensation packages (LPA), and interview-to-offer conversion rates.
   - Department-filtered recruiter rankings and industry-specific hiring splits (Product, IT Services, Banking, Consulting).

3. **Skill Market Demand & Supply Gap Identification**
   - Direct correlation between mandatory technical skills specified in active job postings and verified student proficiencies.
   - Automated identification of high-demand, low-supply skill bottlenecks across cohorts.

4. **Student Readiness Scoring & Candidate Discovery**
   - Multi-factor placement readiness computation (0–100 scale) balancing weighted CGPA, verified skill scores, project portfolios, internships, and interview evaluations.
   - Candidate filtering based on eligibility gates, backlogs, and target job posting profiles.

5. **Conversational Analytics Engine**
   - Context-aware natural language interface connected to the governed semantic layer.
   - Automatic generation of visualizations (interactive bar charts, distribution line charts, and tabular reports with CSV export capabilities).

---

## Governed Semantic Objects

All metrics and analytical views are governed under the `placewise.semantic` schema:

| Object Name | Granularity | Key Metrics & Dimensions |
| :--- | :--- | :--- |
| `semantic.genie_department_performance` | Department × Batch Year | `total_students`, `eligible_students`, `placed_students`, `placement_rate`, `average_ctc_lpa`, `placement_rate_yoy`, `placement_rate_change_points` |
| `semantic.genie_company_intelligence` | Employer | `placements_count`, `openings_count`, `applications_count`, `interview_to_offer_rate`, `average_ctc_lpa`, `highest_ctc_lpa`, `company_type` |
| `semantic.genie_skill_market` | Technical Skill | `job_posting_count`, `student_supply_ratio`, `market_demand_ratio`, `skill_supply_demand_gap`, `high_demand_low_supply_flag` |
| `semantic.genie_student_intelligence` | Student Candidate | `cgpa`, `placement_readiness_score`, `readiness_band`, `preferred_role`, `offers_count`, `placement_status`, `department_code` |
| `semantic.genie_student_job_match` | Student × Job Posting | `skill_match_percentage`, `skill_gap_percentage`, `missing_mandatory_skill_count`, `candidate_fit_band` |

---

## Repository Structure

```
.
├── backend/                        # FastAPI application layer
│   ├── db/                         # SQLite conversation persistence
│   ├── services/
│   │   ├── analytics_service.py    # Analytical metrics aggregation
│   │   ├── databricks_genie.py     # Databricks Genie REST API client
│   │   ├── guardrails.py           # Domain boundary & query moderation
│   │   └── mock_engine.py          # Governed DuckDB fallback engine
│   └── main.py                     # API routing and middleware configuration
├── frontend/                       # React 18 frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── analytics/          # KPI metric cards and summaries
│   │   │   ├── charts/             # Recharts visualization containers
│   │   │   ├── chat/               # Conversational message & composer components
│   │   │   ├── layout/             # Header, navigation, and sidebar components
│   │   │   └── tables/             # Paginated, sortable tabular data views
│   │   ├── context/                # Theme and chat state providers
│   │   └── pages/                  # Dashboard and Chat view controllers
│   ├── package.json
│   └── tailwind.config.js
├── sql/                            # Medallion SQL definitions & transformations
│   ├── ddl/                        # Table DDLs for Bronze, Silver, and Gold
│   └── transformations/            # ETL aggregation and dimension loading scripts
├── synthetic/                      # Synthetic data generation engine
│   ├── config/                     # Statistical distributions and schema parameters
│   ├── generators/                 # Deterministic entity generators (Students, Jobs, etc.)
│   └── run_generator.py            # Master dataset generation script
├── tests/                          # Automated testing suite
│   ├── backend/                    # API endpoints, guardrails, and client tests
│   ├── metrics/                    # Verification of analytical formula correctness
│   └── synthetic/                  # Data integrity and distribution validation
└── databricks.yml                  # Databricks Asset Bundle deployment descriptor
```

---

## Getting Started

### Prerequisites
- **Python**: Version 3.10 or higher
- **Node.js**: Version 18.0 or higher (`npm` included)

### 1. Environment Configuration

Create a `.env` file in the project root:

```ini
# Databricks Credentials (Optional: if omitted, local governed mirror will activate)
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi_your_access_token
DATABRICKS_GENIE_SPACE_ID=your_genie_space_id

# Runtime Configuration
USE_MOCK_BACKEND=false
PORT=8000
```

### 2. Backend Installation & Startup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI orchestration server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The API service will be accessible at `http://localhost:8000`. Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

### 3. Frontend Installation & Startup

```bash
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev -- --host 0.0.0.0 --port 3000
```

Access the user interface at `http://localhost:3000`.

---

## Running the Automated Test Suite

The repository contains automated unit and integration tests covering metric formulas, data quality constraints, API endpoints, and safety guardrails.

```bash
# Run all tests
pytest tests/ -v

# Run metric formula tests specifically
pytest tests/metrics/ -v

# Run backend API and query validation tests
pytest tests/backend/ -v
```

---

## Data Generation Engine

To re-generate or scale the underlying benchmark dataset:

```bash
# Generate small demo profile (1,000 students)
python3 synthetic/run_generator.py --profile small_demo --output data/synthetic

# Generate medium profile (10,000 students)
python3 synthetic/run_generator.py --profile medium_demo --output data/synthetic
```

To reload generated data into the local analytics mirror:

```bash
python3 scripts/load_database.py
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
