# Placewise: Campus Placement Intelligence Platform

Placewise is an institutional analytics and decision support platform built for university placement directorates, department heads, and academic leadership. It centralizes student academic histories, recruitment drive telemetry, verified skill proficiencies, and company hiring trends into a governed data platform powered by Databricks Unity Catalog, an executive analytics dashboard, and a conversational natural language query engine.

---

## 1. Why Placewise Is Needed: The Campus Placement Problem

Campus placement operations in large higher education institutions represent one of the most operationally complex, high-stakes workflows in academia. Placement metrics directly determine institutional rankings (NIRF, NAAC, NBA accreditation), student admissions, corporate partnerships, and university revenue.

Despite this importance, most university placement cells still operate on fragmented, manual systems:

### The Operational Breakdown in Traditional Placement Cells

1. **Spreadsheet Chaos and Data Desynchronization**
   Placement cells frequently track drives across dozens of disconnected Google Sheets and Excel workbooks. Student CGPA updates, backlog clearances from supplementary examinations, and offer acceptances are logged manually. This creates stale data, multiple conflicting versions of truth, and embarrassing errors during live corporate drives (such as shortlisting an ineligible student with an uncleared backlog).

2. **The "Placed" Definition Ambiguity**
   Standard reports often confuse distinct milestones: receiving an initial shortlist, getting an offer letter, accepting an offer, or receiving an internship conversion (PPO). Without strict governance, different departments report different placement numbers to university leadership, causing severe reporting inflation or discrepancy during audit cycles.

3. **Passive Reporting vs. Proactive Remediation**
   Traditional placement reporting is retrospective. Leadership only learns that a department underperformed *after* the placement season concludes in May. By that point, the graduating cohort has left, and it is too late to conduct technical bootcamps, resume workshops, or targeted corporate invite drives.

4. **Curriculum Disconnect from Market Demand**
   Departments design academic syllabi on 3 to 4 year revision cycles, while technology stacks demanded by corporate recruiters shift every 6 to 12 months. Academic departments lack quantitative visibility into which specific frameworks, languages, or tools are being demanded across active job postings versus what students actually know.

Placewise eliminates these failures by establishing a single source of truth grounded in a governed semantic layer.

---

## 2. Why Placewise Works Better Than Normal Search or Standard BI

A common question is why an institution needs Placewise when they already have database keyword search, Google Drive search, or standard dashboard tools.

The table below contrasts standard search and generic BI against Placewise:

| Dimension | Standard Keyword Search / Generic BI | Placewise Placement Intelligence |
| :--- | :--- | :--- |
| **Eligibility Verification** | Searches for strings like "Python" in resumes without verifying real-time CGPA or backlog constraints. | Enforces hard eligibility gates (minimum CGPA, maximum backlogs, approved departments) directly against conformed institutional records. |
| **Metric Accuracy & Grain** | Joining applications, interviews, and offers in naive SQL duplicates rows (fan-out / join explosion), inflating placed student counts. | Uses mathematically conformed Common Table Expressions (CTEs) that compute metrics at their true business grain before joining. |
| **Conversational Understanding** | Matches keywords literally. Searching "hirers in CSE" fails if the table uses the column name `recruiter_id`. | Uses a governed business glossary mapping industry synonyms ("hirers", "recruiters", "companies", "LPA", "package", "CTC", "branch", "department"). |
| **Root-Cause Analysis** | Can only display a chart showing that placements dropped; cannot explain the underlying drivers. | Executes multi-factor reasoning combining drive opening volume, interview round clearance rates, and skill deficit percentages. |
| **Hallucination Prevention** | Generic language models invent statistics, quote arbitrary placement rates, or leak unseen numbers. | Guardrailed orchestration: queries are compiled into deterministic SQL executed exclusively against governed Databricks Unity Catalog tables. |

---

## 3. Walkthrough: Where Placewise Outperforms Traditional Approaches

Here are three real-world scenarios showing how Placewise operates compared to standard search tools:

### Scenario A: Identifying High-Readiness Unplaced Students

* **The Recruiter Request:** A tier-1 product firm announces an impromptu campus drive in February and asks for 30 high-performing students who have not yet secured an offer.
* **Standard Search Failure:** Searching the database for "students without offers" returns hundreds of candidates, including students who opted out of placements, students with active backlogs, or students with very low technical aptitude. The placement officer spends hours manually cross-referencing three different spreadsheets.
* **The Placewise Workflow:**
  1. The user asks: *"Show high-readiness students in CSE and ECE without any job offers."*
  2. Placewise executes against `semantic.genie_student_intelligence`:
     ```sql
     SELECT 
         student_id, 
         full_name, 
         department_code, 
         cgpa, 
         placement_readiness_score, 
         readiness_band, 
         placement_status
     FROM semantic.genie_student_intelligence
     WHERE offers_count = 0 
       AND placement_status IN ('ELIGIBLE', 'ACTIVE')
       AND department_code IN ('CSE', 'ECE')
       AND placement_readiness_score >= 70.0
     ORDER BY placement_readiness_score DESC
     LIMIT 30;
     ```
  3. Result: Within 3 seconds, the placement team has a verified, ranked roster of candidates ready to submit to the company, with zero false shortlists.

---

### Scenario B: Diagnosing a Placement Rate Decline

* **The Problem:** In May, the Dean observes that the Mechanical Engineering department placement rate dropped by 2 percentage points compared to the previous year.
* **Standard BI Failure:** A traditional dashboard shows a line chart going down. It cannot explain whether the issue was fewer companies visiting, students failing coding rounds, lower academic scores, or students declining offers.
* **The Placewise Workflow:**
  1. The Dean asks: *"Why did Mechanical Engineering placement performance decline in 2024?"*
  2. Placewise runs an agent diagnostic checking three underlying layers:
     - Recruiter drive counts and openings in manufacturing and automotive sectors.
     - Technical interview clearance rates for ME students compared to college averages.
     - Skill gap deficits between ME resumes and recruiter requirements.
  3. Placewise returns a structured findings brief:
     - Core campus openings decreased by 14 percent year-over-year.
     - ME technical interview clearance was 42.10 percent versus the 54.18 percent campus average.
     - Primary technical deficits were identified in CAD automation and Python scripting.
  4. The Dean and department head now have actionable data to introduce a 4-week CAD/Python bridge course for the next batch.

---

### Scenario C: Uncovering Recruiter Compensation Reality

* **The Problem:** A company advertises a "30 LPA" package on their campus flyer. In reality, the fixed salary is 6 LPA and the remaining 24 LPA is backloaded stock options vesting over 4 years.
* **Standard Search Failure:** Keyword search finds the flyer text "30 LPA" and reports the company as a top-paying recruiter, misleading students and inflating expectations.
* **The Placewise Workflow:**
  - Placewise enforces canonical data contracts during Silver ingestion, separating CTC into fixed salary, variable pay, and guaranteed first-year payout.
  - The system ranks companies based on verified accepted offer letters, calculating actual median CTC and true student conversion rates.

---

## 4. End-to-End User Journeys

Placewise is designed around the specific daily workflows of university stakeholders:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            User Workflows in Placewise                      │
├────────────────────────┬──────────────────────────┬─────────────────────────┤
│    Placement Officer   │     Department Head      │    Academic Leadership  │
├────────────────────────┼──────────────────────────┼─────────────────────────┤
│ - Live drive monitoring│ - Department benchmark   │ - Institutional ranking │
│ - Recruiter conversion │ - Student readiness rank │ - YoY cohort trajectory │
│ - Candidate matching   │ - Syllabus skill gaps    │ - Department comparisons│
│ - Offer validation     │ - Remedial intervention  │ - Accreditation reports │
└────────────────────────┴──────────────────────────┴─────────────────────────┘
```

### Journey 1: Corporate Drive Coordinator
1. Opens Placewise Executive Dashboard.
2. Selects **Top Recruiters** to inspect historical hiring volumes and interview pass rates for target companies.
3. Uses the conversational chat to ask: *"Which companies hired the most students from CSE and ECE in 2024?"*
4. Downloads clean, sortable CSV data to share with visiting corporate HR teams.

### Journey 2: Department Head (HoD) Review
1. Switches to **Departments** tab on the dashboard.
2. Evaluates placement percentage, placed count, and average compensation package against peer departments.
3. Reviews the **Skill Market** tab to pinpoint high-demand technologies where student supply is deficient.
4. Schedules targeted technical workshops before the primary hiring season starts in August.

---

## 5. Architectural Implementation

### Layer 1: Medallion Architecture on Databricks Unity Catalog

Data flows through four governed stages:

```
[Raw Excel/CSV Ingestion] 
       │
       ▼
┌──────────────────────────────┐
│       Bronze Schema          │  Raw, immutable audit tables with ingestion
│   (placewise.bronze.*)       │  timestamps and source metadata.
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Silver Schema          │  Cleaned, validated Delta tables. Strict primary
│   (placewise.silver.*)       │  and foreign keys, range checks, and quarantine.
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        Gold Schema           │  Dimensional models: Conformed dimensions and facts
│    (placewise.gold.*)        │  aggregated without join inflation.
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Semantic Layer         │  Authoritative, certified business views optimized
│   (placewise.semantic.*)     │  for Databricks Genie natural language execution.
└──────────────────────────────┘
```

### Layer 2: Governed Semantic Objects

Placewise exposes five certified semantic views:

1. **`semantic.genie_department_performance`**
   - Grain: Department by Batch Year.
   - Purpose: Official placement rates, eligible student counts, placed student counts, average package, and year-over-year percentage point shifts.
2. **`semantic.genie_company_intelligence`**
   - Grain: Recruiter / Employer.
   - Purpose: Placements count, job openings count, interview-to-offer clearance percentage, average package (LPA), and hiring selectivity scores.
3. **`semantic.genie_skill_market`**
   - Grain: Technology / Technical Skill.
   - Purpose: Market demand ratio across job postings, student supply ratio across candidate profiles, and supply-demand deficit markers.
4. **`semantic.genie_student_intelligence`**
   - Grain: Individual Student Candidate.
   - Purpose: Academic CGPA, multi-factor readiness score, readiness band, preferred job role, confirmed offer count, and placement status.
5. **`semantic.genie_student_job_match`**
   - Grain: Student Candidate by Active Job Posting.
   - Purpose: Skill match percentage, weighted skill deficit, missing mandatory skills count, and candidate fit classification.

---

## 6. Governed Business Formulas

To eliminate calculation drift across different reports, Placewise standardizes all metrics:

### 1. Official Placement Rate Formula
A student is counted as eligible only if their placement status is active, eligible, or placed (students opting out for higher studies or entrepreneurship are excluded from the denominator):

$$\text{Placement Rate (\%)} = \frac{\text{Count of Placed Students}}{\text{Count of Eligible Students}} \times 100$$

### 2. Multi-Factor Placement Readiness Score (0 to 100)
Rather than relying solely on CGPA, Placewise computes a holistic composite score:

$$\begin{aligned}
\text{Readiness Score} = &\; (0.20 \times \text{Academic Score}) \\
&+ (0.25 \times \text{Verified Skill Score}) \\
&+ (0.10 \times \text{Internship Score}) \\
&+ (0.10 \times \text{Project Score}) \\
&+ (0.20 \times \text{Interview Performance Score}) \\
&+ (0.15 \times \text{Application Conversion Score})
\end{aligned}$$

### 3. Skill Deficit Formula
For any student applying to a job posting:

$$\text{Weighted Deficit} = \frac{\sum \left(\text{Importance Weight} \times \max(0, \text{Required Score} - \text{Student Score})\right)}{\sum \left(\text{Importance Weight} \times \text{Required Score}\right)}$$

$$\text{Skill Match (\%)} = 100 - (\text{Weighted Deficit} \times 100)$$

---

## 7. Safety, Guardrails, and Graceful Handling

Institutional placement systems must remain strictly professional and grounded. Placewise implements defense-in-depth query moderation in `backend/services/guardrails.py`:

1. **Content Safety and Inappropriate Input Rejection**
   Explicit, offensive, or abusive inputs are blocked before running any database queries. The system responds with a polite explanation of its analytical scope.
2. **Domain Boundary Filtering**
   General non-placement questions (such as cooking recipes, general chat, or weather) are intercepted and redirected to placement topics with clickable suggestions.
3. **Transparent System Disclosures**
   Queries asking about underlying models or system architecture return accurate technical disclosures regarding the Databricks Genie and Unity Catalog stack.
4. **No Arbitrary Data Leaks**
   If a user asks an ambiguous question, Placewise does not dump a random department table. It returns an interactive clarification card with suggested analytical pathways.

---

## 8. Repository Layout

```
.
├── backend/
│   ├── db/
│   │   ├── database.py              # SQLite session and message store
│   │   └── schema.sql               # Conversation database schema
│   ├── services/
│   │   ├── analytics_service.py     # KPI aggregation service
│   │   ├── databricks_genie.py      # Databricks Genie REST API client
│   │   ├── guardrails.py            # Safety, profanity, and domain filters
│   │   └── mock_engine.py           # Governed DuckDB local mirror
│   └── main.py                      # FastAPI application and endpoints
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── analytics/           # KPI cards and metric badges
│   │   │   ├── charts/              # Recharts bar and line visualization components
│   │   │   ├── chat/                # Chat messages, composer, evidence drawers
│   │   │   ├── layout/              # Responsive AppLayout, Header, Sidebar
│   │   │   └── tables/              # Paginated, sortable data tables with CSV export
│   │   ├── context/
│   │   │   ├── ChatContext.tsx      # Conversation state management
│   │   │   └── ThemeContext.tsx     # Persistent Light and Dark mode provider
│   │   ├── pages/
│   │   │   ├── ChatPage.tsx         # Natural language analytics interface
│   │   │   └── DashboardPage.tsx    # Executive KPI and domain tables view
│   │   ├── services/
│   │   │   └── placewiseApi.ts      # REST API client
│   │   └── App.tsx
│   ├── package.json
│   └── tailwind.config.js
├── sql/
│   ├── ddl/                         # DDLs for Bronze, Silver, Gold, and Semantic
│   └── transformations/             # Idempotent ETL scripts with CTEs
├── synthetic/
│   ├── config/                      # Statistical profiles and role definitions
│   ├── generators/                  # Generator modules for students, companies, etc.
│   └── run_generator.py             # CLI generation orchestrator
├── tests/
│   ├── backend/                     # API, guardrail, and SQLite tests
│   ├── metrics/                     # Unit tests for placement rate and readiness formulas
│   └── synthetic/                   # Distribution and referential integrity tests
├── databricks.yml                   # Databricks Asset Bundle specification
└── requirements.txt                 # Python dependencies
```

---

## 9. Getting Started

### Prerequisites
- Python 3.10 or higher
- Node.js 18.0 or higher with npm

### Step 1: Clone and Configure Environment

```bash
git clone https://github.com/Arya-Akshat/Placewise-Placement-Intelligence-.git
cd Placewise-Placement-Intelligence-
```

Create a `.env` file in the root directory:

```ini
# Databricks Workspace (Optional: when omitted, local governed mirror runs)
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi_your_access_token
DATABRICKS_GENIE_SPACE_ID=your_genie_space_id

# Local Runtime
USE_MOCK_BACKEND=false
PORT=8000
```

### Step 2: Start the Backend Service

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server on port 8000
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. You can test endpoints via the Swagger UI at `http://localhost:8000/docs`.

### Step 3: Start the Frontend Application

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server on port 3000
npm run dev -- --host 0.0.0.0 --port 3000
```

Open your browser at `http://localhost:3000`.

---

## 10. Automated Testing and Verification

Placewise maintains a comprehensive automated testing suite:

```bash
# Run all automated tests
pytest tests/ -v

# Run metric calculation tests specifically
pytest tests/metrics/ -v

# Run backend API and safety guardrail tests
pytest tests/backend/ -v
```

All 36 core test suites must pass before any code is merged into the main branch.

---

## 11. Synthetic Data Generation Engine

To generate fresh benchmark datasets or test different scale profiles:

```bash
# Generate 1,000 students (development)
python3 synthetic/run_generator.py --profile small_demo --output data/synthetic

# Generate 10,000 students (testing)
python3 synthetic/run_generator.py --profile medium_demo --output data/synthetic

# Rebuild local DuckDB analytical database
python3 scripts/load_database.py
```

---

## 12. License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
