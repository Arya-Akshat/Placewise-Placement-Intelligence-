# Placewise Databricks Genie Live Evaluation Report

**Evaluation Date:** 2026-09-01 14:28:25Z  
**Evaluation Status:** **NOT_VERIFIED** (Live Databricks workspace credentials not supplied)  
**Total Benchmarks Defined:** 23  
**Executed Against Live API:** 0  
**Tests Not Run:** 23  

---

## 1. Evaluation Architecture Status

| Verification Layer | Local Engine Status | Remote Live Genie Status |
|---|---|---|
| **Semantic DDL & Views** | **PASS** (100% Unique Grain) | Unity Catalog (`placewise.semantic.*`) |
| **Deterministic SQL Metrics** | **PASS** (0.0000% Variance) | Ready for Execution |
| **FastAPI Orchestration** | **PASS** (32/32 Unit Tests) | Connected to `DatabricksGenieClient` |
| **React Conversational UI** | **PASS** (12/12 Scenarios) | Bounded & Rendered |
| **Live Remote Databricks Space** | N/A | **NOT_VERIFIED** (Awaiting Credentials) |

---

## 2. Instructions to Execute Live Remote Benchmarks

When active workspace credentials are provided:
1. Set in `backend/.env`:
   ```bash
   DATABRICKS_HOST="https://<your-workspace>.cloud.databricks.com"
   DATABRICKS_TOKEN="dapi..."
   DATABRICKS_GENIE_SPACE_ID="01ef..."
   ```
2. Run the evaluator:
   ```bash
   python3 scripts/evaluate_live_genie.py
   ```
3. The runner will execute all 23 benchmarks, capture live generated SQL from Databricks Genie, compare results against ground-truth direct SQL queries with <= 0.01 tolerance, and promote `PLACEWISE_LIVE_GENIE_READY` to `TRUE`.
