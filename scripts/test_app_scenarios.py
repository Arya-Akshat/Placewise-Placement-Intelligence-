#!/usr/bin/env python3
"""
PLACEWISE — End-to-End Application Integration & Scenario Test Runner
====================================================================
Tests the complete backend conversation lifecycle across all 12 scenarios:
  - Conversation initiation
  - Follow-up context preservation
  - KPI & Table attachments
  - Chart generation metadata
  - Clarification triggers & quick-reply payloads
  - Agent Mode multi-step reasoning evidence cards
  - Large result set safety & truncation bounding
"""

import os, sys, time, json, uuid
from fastapi.testclient import TestClient

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set mock mode for offline test runner
os.environ["USE_MOCK_BACKEND"] = "true"

from backend.main import app

client = TestClient(app)

print("=" * 70)
print("  PLACEWISE — End-to-End 12 Scenario Verification Suite")
print("=" * 70)

scenarios = [
    {
        "id": "SCENARIO 1",
        "question": "What is the placement rate for CSE in 2024?",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: "51.49%" in m.get("content", "") and m.get("attachment", {}).get("kpis") is not None,
        "type": "KPI & Placement Metric"
    },
    {
        "id": "SCENARIO 2",
        "question": "How does that compare with ECE?",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: "48.86%" in m.get("content", "") and m.get("attachment", {}).get("recommended_visualization") == "BAR",
        "type": "Follow-Up Comparison"
    },
    {
        "id": "SCENARIO 3",
        "question": "What are the top 10 demanded skills?",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: m.get("attachment", {}).get("table_data") is not None and len(m["attachment"]["table_data"]["rows"]) > 0,
        "type": "Skill Market Ranking"
    },
    {
        "id": "SCENARIO 4",
        "question": "Show high-readiness students without offers.",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: m.get("attachment", {}).get("table_data") is not None and len(m["attachment"]["table_data"]["rows"]) > 0,
        "type": "Student Capability Discovery"
    },
    {
        "id": "SCENARIO 5",
        "question": "Which companies hired the most students?",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: m.get("attachment", {}).get("table_data") is not None and m["attachment"]["recommended_visualization"] == "BAR",
        "type": "Recruiter Analytics"
    },
    {
        "id": "SCENARIO 6",
        "question": "Which departments improved placement rate?",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: m.get("attachment", {}).get("table_data") is not None and len(m["attachment"]["table_data"]["rows"]) > 0,
        "type": "YoY Trend Benchmark"
    },
    {
        "id": "SCENARIO 7",
        "question": "Which skills have high demand but low supply?",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: m.get("attachment", {}).get("table_data") is not None,
        "type": "Skill Gap Analysis"
    },
    {
        "id": "SCENARIO 8",
        "question": "Find the strongest Data Engineering candidates.",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: m.get("attachment", {}).get("table_data") is not None and len(m["attachment"]["table_data"]["rows"]) > 0,
        "type": "Candidate Recommendation"
    },
    {
        "id": "SCENARIO 9",
        "question": "What is the placement rate?",
        "expected_status": "CLARIFICATION_REQUIRED",
        "expected_check": lambda m: m.get("clarification") is not None and len(m["clarification"]["options"]) >= 2,
        "type": "Ambiguity Clarification Trigger"
    },
    {
        "id": "SCENARIO 10",
        "question": "Which company performed best?",
        "expected_status": "CLARIFICATION_REQUIRED",
        "expected_check": lambda m: m.get("clarification") is not None and len(m["clarification"]["options"]) >= 2,
        "type": "Metric Ambiguity Clarification"
    },
    {
        "id": "SCENARIO 11",
        "question": "Why did Mechanical placement performance change?",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: m.get("agent_analysis") is not None and len(m["agent_analysis"]["evidence"]) >= 3,
        "type": "Agent Mode Multi-Step Reasoning"
    },
    {
        "id": "SCENARIO 12",
        "question": "Show me all student-job matches.",
        "expected_status": "COMPLETED",
        "expected_check": lambda m: m.get("attachment", {}).get("table_data", {}).get("truncated") == True and m["attachment"]["table_data"]["total_row_count"] == 125002500 and len(m["attachment"]["table_data"]["rows"]) <= 10,
        "type": "Large Result Set Bounding Protection"
    }
]

# 1. Start conversation
res1 = client.post("/api/v1/conversations", json={
    "content": "Init conversation",
    "client_request_id": f"req_{uuid.uuid4().hex}"
})
conv = res1.json()
conv_id = conv["conversation_id"]

all_passed = True
results = []

for sc in scenarios:
    t0 = time.time()
    try:
        res = client.post(f"/api/v1/conversations/{conv_id}/messages", json={
            "content": sc["question"],
            "client_request_id": f"req_{uuid.uuid4().hex}"
        })
        msg = res.json()
        latency_ms = round((time.time() - t0) * 1000, 2)
        
        status_match = (msg.get("status") == sc["expected_status"])
        check_match = sc["expected_check"](msg)
        
        passed = status_match and check_match
        if not passed:
            all_passed = False
            
        status_str = "PASS" if passed else "FAIL"
    except Exception as e:
        latency_ms = round((time.time() - t0) * 1000, 2)
        status_str = f"FAIL ({str(e)})"
        all_passed = False

    results.append({
        "id": sc["id"],
        "question": sc["question"],
        "type": sc["type"],
        "latency_ms": latency_ms,
        "status": status_str
    })
    print(f"  [{status_str:<4}] {sc['id']}: \"{sc['question']}\" — {latency_ms}ms ({sc['type']})")

print("=" * 70)
print(f"  ALL 12 END-TO-END SCENARIOS: {'100% PASSED' if all_passed else 'FAILED'}")
print("=" * 70)

sys.exit(0 if all_passed else 1)
