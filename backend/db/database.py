"""
PLACEWISE — Persistent Storage Engine (SQLite)
==============================================
Persists conversation history, message metadata, and client idempotency records.
"""

import sqlite3, os, json, time
from typing import List, Optional, Dict, Any

DB_FILE = os.path.join(os.path.dirname(__file__), "../../data/conversations.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            genie_conversation_id TEXT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE'
        );
    """)

    # 2. Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            genie_message_id TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            attachment_json TEXT,
            clarification_json TEXT,
            agent_analysis_json TEXT,
            follow_up_suggestions_json TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
        );
    """)

    # 3. Idempotency table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS idempotency_records (
            client_request_id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            message_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    conn.commit()
    conn.close()

# Initialize tables immediately
init_db()

def create_conversation(conversation_id: str, title: str, user_id: str = "default_user", genie_conversation_id: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    cursor.execute("""
        INSERT INTO conversations (conversation_id, genie_conversation_id, user_id, title, created_at, updated_at, status)
        VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE');
    """, (conversation_id, genie_conversation_id, user_id, title, now, now))
    
    conn.commit()
    conn.close()
    return {
        "conversation_id": conversation_id,
        "genie_conversation_id": genie_conversation_id,
        "user_id": user_id,
        "title": title,
        "created_at": now,
        "updated_at": now,
        "status": "ACTIVE",
        "messages": []
    }

def update_genie_conversation_id(conversation_id: str, genie_conversation_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE conversations SET genie_conversation_id = ?, updated_at = ? WHERE conversation_id = ?;
    """, (genie_conversation_id, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), conversation_id))
    conn.commit()
    conn.close()

def save_message(conversation_id: str, message: Dict[str, Any], genie_message_id: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    cursor.execute("""
        INSERT OR REPLACE INTO messages (
            message_id, conversation_id, genie_message_id, role, content, status, created_at,
            attachment_json, clarification_json, agent_analysis_json, follow_up_suggestions_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        message["message_id"],
        conversation_id,
        genie_message_id,
        message["role"],
        message["content"],
        message["status"],
        message.get("created_at", now),
        json.dumps(message["attachment"]) if message.get("attachment") else None,
        json.dumps(message["clarification"]) if message.get("clarification") else None,
        json.dumps(message["agent_analysis"]) if message.get("agent_analysis") else None,
        json.dumps(message["follow_up_suggestions"]) if message.get("follow_up_suggestions") else None
    ))

    cursor.execute("""
        UPDATE conversations SET updated_at = ? WHERE conversation_id = ?;
    """, (now, conversation_id))

    conn.commit()
    conn.close()

def get_conversation_by_id(conversation_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM conversations WHERE conversation_id = ?;", (conversation_id,))
    conv_row = cursor.fetchone()
    if not conv_row:
        conn.close()
        return None

    cursor.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC;", (conversation_id,))
    msg_rows = cursor.fetchall()

    messages = []
    for r in msg_rows:
        messages.append({
            "message_id": r["message_id"],
            "role": r["role"],
            "content": r["content"],
            "status": r["status"],
            "created_at": r["created_at"],
            "attachment": json.loads(r["attachment_json"]) if r["attachment_json"] else None,
            "clarification": json.loads(r["clarification_json"]) if r["clarification_json"] else None,
            "agent_analysis": json.loads(r["agent_analysis_json"]) if r["agent_analysis_json"] else None,
            "follow_up_suggestions": json.loads(r["follow_up_suggestions_json"]) if r["follow_up_suggestions_json"] else None
        })

    conn.close()
    return {
        "conversation_id": conv_row["conversation_id"],
        "genie_conversation_id": conv_row["genie_conversation_id"],
        "user_id": conv_row["user_id"],
        "title": conv_row["title"],
        "created_at": conv_row["created_at"],
        "updated_at": conv_row["updated_at"],
        "status": conv_row["status"],
        "messages": messages
    }

def list_recent_conversations(user_id: str = "default_user", limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.conversation_id, c.title, c.created_at, c.updated_at,
               (SELECT content FROM messages WHERE conversation_id = c.conversation_id ORDER BY created_at DESC LIMIT 1) AS last_message,
               (SELECT COUNT(*) FROM messages WHERE conversation_id = c.conversation_id) AS message_count
        FROM conversations c
        WHERE c.user_id = ?
        ORDER BY c.updated_at DESC
        LIMIT ?;
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()

    return [{
        "conversation_id": r["conversation_id"],
        "title": r["title"],
        "created_at": r["created_at"],
        "updated_at": r["updated_at"],
        "last_message": r["last_message"] or "",
        "message_count": r["message_count"]
    } for r in rows]

def check_idempotency(client_request_id: str) -> Optional[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT message_id FROM idempotency_records WHERE client_request_id = ?;", (client_request_id,))
    row = cursor.fetchone()
    conn.close()
    return row["message_id"] if row else None

def record_idempotency(client_request_id: str, conversation_id: str, message_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO idempotency_records (client_request_id, conversation_id, message_id, created_at)
        VALUES (?, ?, ?, ?);
    """, (client_request_id, conversation_id, message_id, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    conn.commit()
    conn.close()
