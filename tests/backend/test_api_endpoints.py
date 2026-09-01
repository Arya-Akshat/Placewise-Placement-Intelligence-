import pytest, os, uuid
from fastapi.testclient import TestClient

os.environ["USE_MOCK_BACKEND"] = "true"
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["backend"] is True

def test_start_and_follow_up_conversation_mock(monkeypatch):
    monkeypatch.setenv("USE_MOCK_BACKEND", "true")
    # 1. Start conversation
    req_id_1 = f"req_{uuid.uuid4().hex}"
    res1 = client.post("/api/v1/conversations", json={
        "content": "What is the placement rate for CSE in 2024?",
        "client_request_id": req_id_1
    })
    assert res1.status_code == 200
    conv = res1.json()
    assert "conversation_id" in conv
    assert len(conv["messages"]) == 2
    assert "51.49%" in conv["messages"][1]["content"]

    cid = conv["conversation_id"]

    # 2. Send follow-up
    req_id_2 = f"req_{uuid.uuid4().hex}"
    res2 = client.post(f"/api/v1/conversations/{cid}/messages", json={
        "content": "How does that compare with ECE?",
        "client_request_id": req_id_2
    })
    assert res2.status_code == 200
    msg = res2.json()
    assert "48.86%" in msg["content"]
    assert msg["attachment"]["recommended_visualization"] == "BAR"

def test_clarification_endpoint_mock(monkeypatch):
    monkeypatch.setenv("USE_MOCK_BACKEND", "true")
    res = client.post("/api/v1/conversations", json={
        "content": "What is the placement rate?",
        "client_request_id": f"req_{uuid.uuid4().hex}"
    })
    assert res.status_code == 200
    conv = res.json()
    asst_msg = conv["messages"][1]
    assert asst_msg["status"] == "CLARIFICATION_REQUIRED"
    assert asst_msg["clarification"] is not None
    assert len(asst_msg["clarification"]["options"]) >= 2
