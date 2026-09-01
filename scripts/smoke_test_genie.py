#!/usr/bin/env python3
"""
PLACEWISE — High-Value Genie Smoke Test Suite
============================================
Executes high-value placement queries, candidate recommendations,
and department benchmarks against the curated semantic layer.

Saves structured test execution output to reports/genie_smoke_test.json.
"""

import duckdb, json, time, os, sys

DB_PATH = "data/placewise.duckdb"
con = duckdb.connect(DB_PATH)

print("=" * 65)
print("  PLACEWISE — Genie Agent Smoke Test Suite")
print("=" * 65)

smoke_tests = [
    {
        "test_id": "SMOKE-01",
        "question": "What is CSE placement rate for 2024?",
        "intent": "Department Placement Rate",
        "target_object": "semantic.genie_department_performance",
        "sql": "SELECT department_code, graduation_year, total_students, eligible_students, placed_students, placement_rate FROM semantic.genie_department_performance WHERE department_code = 'CSE' AND graduation_year = 2024;"
    },
    {
        "test_id": "SMOKE-02",
        "question": "Which company hired the most students?",
        "intent": "Top Hiring Companies",
        "target_object": "semantic.genie_company_intelligence",
        "sql": "SELECT company_name, industry, company_type, placements_count, average_ctc_lpa FROM semantic.genie_company_intelligence ORDER BY placements_count DESC LIMIT 5;"
    },
    {
        "test_id": "SMOKE-03",
        "question": "What are the top demanded skills?",
        "intent": "Market Skill Demand Ranking",
        "target_object": "semantic.genie_skill_market",
        "sql": "SELECT demand_rank, skill_name, skill_category, job_posting_count, company_count FROM semantic.genie_skill_market ORDER BY demand_rank ASC LIMIT 5;"
    },
    {
        "test_id": "SMOKE-04",
        "question": "Show high-readiness students without offers.",
        "intent": "Unplaced High Readiness Candidates",
        "target_object": "semantic.genie_student_intelligence",
        "sql": "SELECT student_id, full_name, department_code, cgpa, academic_score, skill_score, placement_readiness_score, offers_count FROM semantic.genie_student_intelligence WHERE offers_count = 0 AND placement_status IN ('ELIGIBLE','ACTIVE') ORDER BY placement_readiness_score DESC LIMIT 5;"
    },
    {
        "test_id": "SMOKE-05",
        "question": "Which departments improved placement rate?",
        "intent": "Year-over-Year Improvement",
        "target_object": "semantic.genie_department_performance",
        "sql": "SELECT department_code, graduation_year, placement_rate, placement_rate_yoy, placement_rate_change_points FROM semantic.genie_department_performance WHERE graduation_year = 2024 AND placement_rate_change_points > 0 ORDER BY placement_rate_change_points DESC;"
    }
]

results = []
all_passed = True

for st in smoke_tests:
    t0 = time.time()
    try:
        df = con.execute(st["sql"]).df()
        duration_ms = round((time.time() - t0) * 1000, 2)
        rows = len(df)
        sample = df.to_dict(orient="records")
        status = "PASS" if rows > 0 else "FAIL (No rows returned)"
    except Exception as e:
        duration_ms = round((time.time() - t0) * 1000, 2)
        rows = 0
        sample = str(e)
        status = f"FAIL ({str(e)})"
        all_passed = False

    results.append({
        "test_id": st["test_id"],
        "question": st["question"],
        "intent": st["intent"],
        "target_object": st["target_object"],
        "sql": st["sql"],
        "duration_ms": duration_ms,
        "rows": rows,
        "sample": sample,
        "status": status
    })
    print(f"  [{status}] {st['test_id']}: \"{st['question']}\" — {duration_ms}ms ({rows} rows)")

os.makedirs("reports", exist_ok=True)
report_path = "reports/genie_smoke_test.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump({
        "suite": "Placewise Genie Smoke Tests",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_tests": len(results),
        "passed": sum(1 for r in results if r["status"] == "PASS"),
        "results": results
    }, f, indent=2)

print(f"\n✓ Smoke test results saved to: {report_path}")
print("=" * 65)
sys.exit(0 if all_passed else 1)
