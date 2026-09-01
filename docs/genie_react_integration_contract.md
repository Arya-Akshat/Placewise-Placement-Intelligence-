# Placewise Databricks Genie Conversation API & React Frontend Integration Contract

**Contract Version:** 2.0  
**Target System:** Placewise React Conversational Web Client $\to$ Databricks Genie API  
**Status:** Certified & Ready for Frontend Implementation  
**Agent Identifier:** `genie_space_placewise_placement_intelligence_v2`  

---

## 1. Architecture Overview

In the upcoming frontend implementation phase, the React conversational interface interacts exclusively with the **Databricks Genie Conversation API**. The React UI never executes raw SQL directly against the database; instead, natural language messages are submitted to the Genie Agent, which returns grounded SQL queries, tabular query results, synthesized explanations, and chart recommendations.

```
┌────────────────────────────────────────────────────────┐
│               Placewise React Frontend                 │
│      (Chat Window, Data Tables, Analytical Charts)     │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS / REST (JSON)
                            ▼
┌────────────────────────────────────────────────────────┐
│          Placewise Node.js / FastAPI Backend           │
│           (OAuth Token Management & Proxy)             │
└───────────────────────────┬────────────────────────────┘
                            │ Databricks REST API (v2.0)
                            ▼
┌────────────────────────────────────────────────────────┐
│            Databricks Genie Agent (Space)              │
│       ID: genie_space_placewise_placement_intel        │
└───────────────────────────┬────────────────────────────┘
                            │ Governed SQL Queries
                            ▼
┌────────────────────────────────────────────────────────┐
│              PLACEWISE.SEMANTIC Views                  │
│  (genie_student, genie_company, genie_department, ...) │
└────────────────────────────────────────────────────────┘
```

---

## 2. API Endpoints Specification

### 2.1 Start New Conversation
* **Method**: `POST`
* **Endpoint**: `/api/2.0/genie/spaces/{space_id}/start-conversation`
* **Request Payload**:
  ```json
  {
    "content": "What is the placement rate for CSE in 2024?"
  }
  ```
* **Response Payload (HTTP 200 OK)**:
  ```json
  {
    "conversation_id": "conv_01j6xyz89abc",
    "message_id": "msg_01j6xyz89def",
    "status": "COMPLETED",
    "content": "CSE placement rate for the 2024 graduating cohort was 51.49%, based on 1,159 placed students out of 2,251 eligible students.",
    "attachments": [
      {
        "type": "QUERY",
        "query": {
          "query_id": "qry_01j6xyz89ghi",
          "query_text": "SELECT department_code, graduation_year, total_students, eligible_students, placed_students, placement_rate FROM placewise.semantic.genie_department_performance WHERE department_code = 'CSE' AND graduation_year = 2024;",
          "description": "CSE 2024 placement performance"
        }
      }
    ]
  }
  ```

### 2.2 Send Follow-Up Message in Conversation
* **Method**: `POST`
* **Endpoint**: `/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages`
* **Request Payload**:
  ```json
  {
    "content": "How does that compare with ECE?"
  }
  ```
* **Response Payload (HTTP 200 OK)**:
  ```json
  {
    "conversation_id": "conv_01j6xyz89abc",
    "message_id": "msg_01j6xyz90jkl",
    "status": "COMPLETED",
    "content": "ECE placement rate for the 2024 batch was 48.86% (794 placed out of 1,625 eligible students), which is 2.63 percentage points lower than CSE (51.49%).",
    "attachments": [
      {
        "type": "QUERY",
        "query": {
          "query_id": "qry_01j6xyz90mno",
          "query_text": "SELECT department_code, graduation_year, total_students, eligible_students, placed_students, placement_rate FROM placewise.semantic.genie_department_performance WHERE department_code IN ('CSE', 'ECE') AND graduation_year = 2024 ORDER BY placement_rate DESC;"
        }
      }
    ]
  }
  ```

### 2.3 Fetch Query Result Set (Tabular Execution Data)
* **Method**: `GET`
* **Endpoint**: `/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/query-result`
* **Response Payload (HTTP 200 OK)**:
  ```json
  {
    "manifest": {
      "schema": {
        "columns": [
          {"name": "department_code", "type_text": "STRING"},
          {"name": "graduation_year", "type_text": "INT"},
          {"name": "total_students", "type_text": "BIGINT"},
          {"name": "eligible_students", "type_text": "BIGINT"},
          {"name": "placed_students", "type_text": "BIGINT"},
          {"name": "placement_rate", "type_text": "DOUBLE"}
        ]
      },
      "total_row_count": 2
    },
    "result": {
      "data_array": [
        ["CSE", 2024, 2529, 2251, 1159, 51.49],
        ["ECE", 2024, 1859, 1625, 794, 48.86]
      ]
    }
  }
  ```

---

## 3. UI Component Rendering Contracts

### 3.1 Response Type Handling in React

| Genie Attachment Type | React UI Component | Rendering Logic |
|---|---|---|
| `QUERY` + `data_array` ($\le 10$ rows, $\ge 2$ numeric cols) | `<PlacementBarChart />` | Renders a bar or line chart (e.g. Placement Rate by Branch). |
| `QUERY` + `data_array` ($> 10$ rows or student lists) | `<PlacementDataTable />` | Interactive sortable, filterable table with pagination and CSV export. |
| `CLARIFICATION_REQUIRED` | `<ClarificationPrompt />` | Render quick-reply suggestion chips (e.g. `[2024 Batch]`, `[2023 Batch]`, `[All Branches]`). |
| `AGENT_MODE_PLAN` | `<AgentReasoningAccordion />` | Collapsible multi-step reasoning tree showing subqueries and evidence cards. |

---

## 4. Authentication & Security
1. **OAuth M2M Service Principal**: The intermediate API backend uses a Databricks Service Principal with OAuth token rotation (`Bearer ${DATABRICKS_TOKEN}`).
2. **No User Credentials in Frontend**: Tokens never touch the browser; the React frontend connects to the backend proxy via session cookies or JWT.
3. **PII Redaction**: Student identity fields default to `student_id` / `university_roll_no` unless an authorized user specifically requests detailed contact info.

---

## 5. Error Handling & Timeout Budgets
* **Timeout SLA**: 30 seconds for standard queries; 90 seconds for multi-step Agent Mode decompositions.
* **Retry Strategy**: Exponential backoff on HTTP 429 (Rate Limit) with jitter ($1\text{s}, 2\text{s}, 4\text{s}$).
* **Circuit Breaker**: Degrade gracefully to trusted asset pre-cached responses if the SQL Warehouse is in cold startup.
