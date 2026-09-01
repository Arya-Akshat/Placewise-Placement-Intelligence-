import pytest, time
from backend.db import database as db

def test_sqlite_conversation_lifecycle():
    cid = f"test_conv_{int(time.time()*1000)}"
    conv = db.create_conversation(conversation_id=cid, title="Test Conversation")
    assert conv["conversation_id"] == cid
    assert conv["title"] == "Test Conversation"

    msg = {
        "message_id": f"msg_{cid}",
        "role": "user",
        "content": "Hello Placewise",
        "status": "COMPLETED"
    }
    db.save_message(cid, msg)

    retrieved = db.get_conversation_by_id(cid)
    assert retrieved is not None
    assert len(retrieved["messages"]) == 1
    assert retrieved["messages"][0]["content"] == "Hello Placewise"

def test_sqlite_idempotency():
    req_id = f"req_unique_{int(time.time()*1000)}"
    assert db.check_idempotency(req_id) is None

    db.record_idempotency(req_id, "conv_1", "msg_1")
    assert db.check_idempotency(req_id) == "msg_1"
