from backend.services.analytics_service import get_analytics_overview
"""
PLACEWISE — Production Application Orchestration Layer (FastAPI)
================================================================
Thin orchestration service mediating between React frontend and Databricks Genie:
  - POST /api/v1/conversations
  - POST /api/v1/conversations/{conversation_id}/messages
  - GET  /api/v1/conversations/{conversation_id}
  - GET  /api/v1/conversations
  - GET  /api/v1/health
  - GET  /api/v1/health/ready
"""

import os, sys, time, uuid, json, re, asyncio, logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Database & Genie Client
from backend.db import database as db
from backend.services.databricks_genie import DatabricksGenieClient, DatabricksGenieError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PlacewiseAPI")

# Initialize Genie Client
genie_client = DatabricksGenieClient()

# Per-conversation concurrency locks
CONVERSATION_LOCKS: Dict[str, asyncio.Lock] = {}

def get_conversation_lock(conv_id: str) -> asyncio.Lock:
    if conv_id not in CONVERSATION_LOCKS:
        CONVERSATION_LOCKS[conv_id] = asyncio.Lock()
    return CONVERSATION_LOCKS[conv_id]

# -----------------------------------------------------------------------------
# FastAPI App & Security Configuration
# -----------------------------------------------------------------------------

app = FastAPI(
    title="Placewise Placement Intelligence API",
    version="2.0.0",
    description="Production conversational orchestration service connecting React to Databricks Genie"
)

# CORS Configuration
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "User-Agent"],
)

# -----------------------------------------------------------------------------
# Authentication & Role Authorization Placeholder
# -----------------------------------------------------------------------------

class UserContext(BaseModel):
    user_id: str = "placement_officer_01"
    role: str = "Placement Officer" # Student, Placement Officer, Faculty, Recruiter, Admin
    department_scope: Optional[str] = None

def get_current_user(request: Request) -> UserContext:
    # Future SSO / OIDC JWT validation hook
    auth_header = request.headers.get("Authorization")
    return UserContext(user_id="default_user", role="Placement Officer")

# -----------------------------------------------------------------------------
# Pydantic Request & Response Schemas
# -----------------------------------------------------------------------------

class ColumnDef(BaseModel):
    name: str
    type_text: str
    display_name: str

class TableData(BaseModel):
    columns: List[ColumnDef]
    rows: List[Dict[str, Any]]
    total_row_count: int
    truncated: bool = False

class KpiItem(BaseModel):
    label: str
    value: str
    change: Optional[str] = None
    subtext: Optional[str] = None

class EvidenceCard(BaseModel):
    title: str
    value: str
    description: str
    metric_name: str

class AgentAnalysisData(BaseModel):
    summary: str
    findings: List[str]
    evidence: List[EvidenceCard]
    supporting_chart_type: Optional[str] = None

class ClarificationOption(BaseModel):
    id: str
    label: str
    value: str

class ClarificationPayload(BaseModel):
    prompt: str
    options: List[ClarificationOption]

class QueryAttachment(BaseModel):
    query_id: str
    query_text: Optional[str] = None
    source_object: str
    target_metric: Optional[str] = None
    table_data: Optional[TableData] = None
    recommended_visualization: Optional[str] = None
    kpis: Optional[List[KpiItem]] = None

class Message(BaseModel):
    message_id: str
    role: str
    content: str
    status: str
    created_at: str
    attachment: Optional[QueryAttachment] = None
    clarification: Optional[ClarificationPayload] = None
    agent_analysis: Optional[AgentAnalysisData] = None
    follow_up_suggestions: Optional[List[str]] = None

class ConversationResponse(BaseModel):
    conversation_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Message]

class StartConversationRequest(BaseModel):
    content: Optional[str] = None
    client_request_id: Optional[str] = None

class SendMessageRequest(BaseModel):
    content: str
    client_request_id: Optional[str] = None

# -----------------------------------------------------------------------------
# Title Generation Utility
# -----------------------------------------------------------------------------

def clean_title_from_prompt(prompt: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", prompt).strip()
    words = cleaned.split()
    title = " ".join(words[:6])
    if len(title) > 45:
        title = title[:42] + "..."
    return title or "New Conversation"

# -----------------------------------------------------------------------------
# REST Endpoints
# -----------------------------------------------------------------------------

@app.get("/api/v1/health")
def health_check():
    db_exists = os.path.exists(os.path.join(os.path.dirname(__file__), "../data/placewise.duckdb"))
    return {
        "status": "HEALTHY",
        "backend": True,
        "duckdb_mirror": db_exists,
        "genie_configured": genie_client.is_configured
    }

@app.get("/api/v1/health/ready")
def readiness_check():
    is_ready, detail = genie_client.check_ready()
    use_mock = os.environ.get("USE_MOCK_BACKEND", "").lower() == "true"
    if not is_ready and not use_mock:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Genie service not ready: {detail}"
        )
    return {
        "status": "READY",
        "mode": "LIVE" if is_ready else "MOCK",
        "detail": detail
    }


@app.get("/api/v1/analytics/overview")
def get_dashboard_analytics():
    return get_analytics_overview()

@app.get("/api/v1/conversations")
def list_conversations(current_user: UserContext = Depends(get_current_user)):
    return {"conversations": db.list_recent_conversations(user_id=current_user.user_id)}

@app.get("/api/v1/conversations/{conversation_id}")
def get_conversation(conversation_id: str, current_user: UserContext = Depends(get_current_user)):
    conv = db.get_conversation_by_id(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@app.post("/api/v1/conversations")
async def start_conversation(
    req: StartConversationRequest,
    current_user: UserContext = Depends(get_current_user)
):
    # Idempotency check
    if req.client_request_id:
        existing_msg_id = db.check_idempotency(req.client_request_id)
        if existing_msg_id:
            logger.info(f"Duplicate client request ID '{req.client_request_id}' detected.")
            # Return current conversation state
            for c in db.list_recent_conversations(user_id=current_user.user_id):
                full_c = db.get_conversation_by_id(c["conversation_id"])
                if full_c and any(m["message_id"] == existing_msg_id for m in full_c["messages"]):
                    return full_c

    placewise_cid = f"conv_{uuid.uuid4().hex[:12]}"
    title = clean_title_from_prompt(req.content) if req.content else "New Placement Conversation"
    
    # Create persistent session
    conv = db.create_conversation(
        conversation_id=placewise_cid,
        title=title,
        user_id=current_user.user_id
    )

    if not req.content:
        return conv

    # Process first message
    user_msg_id = f"msg_user_{uuid.uuid4().hex[:12]}"
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    user_msg = {
        "message_id": user_msg_id,
        "role": "user",
        "content": req.content,
        "status": "COMPLETED",
        "created_at": now
    }
    db.save_message(placewise_cid, user_msg)
    if req.client_request_id:
        db.record_idempotency(req.client_request_id, placewise_cid, user_msg_id)

    # Route to Databricks Genie or Mock Fallback
    use_mock = os.environ.get("USE_MOCK_BACKEND", "").lower() == "true"
    if not use_mock and genie_client.is_configured:
        try:
            logger.info(f"Starting Databricks Genie conversation for space '{genie_client.space_id}'...")
            raw_start = genie_client.start_conversation(req.content)
            genie_cid = raw_start.get("conversation_id") or raw_start.get("id")
            genie_mid = raw_start.get("message_id") or (raw_start.get("message") or {}).get("id")
            
            db.update_genie_conversation_id(placewise_cid, genie_cid)

            # Poll message if not completed
            raw_msg = genie_client.poll_message_completion(genie_cid, genie_mid)
            
            # Fetch query results if query attachment exists
            query_result = None
            if raw_msg.get("status") == "COMPLETED":
                query_result = genie_client.fetch_query_result(genie_cid, genie_mid)

            asst_msg = genie_client.normalize_genie_message(raw_msg, query_result)
            db.save_message(placewise_cid, asst_msg, genie_message_id=genie_mid)

        except DatabricksGenieError as e:
            logger.warning(f"Genie upstream error: {e.message}. Executing governed semantic engine...")
            from backend.services.mock_engine import process_mock_query
            asst_msg = process_mock_query(req.content, [user_msg])
            db.save_message(placewise_cid, asst_msg)
    elif use_mock:
        # Development Mock Mode
        from backend.services.mock_engine import process_mock_query
        asst_msg = process_mock_query(req.content, [user_msg])
        db.save_message(placewise_cid, asst_msg)
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Databricks Genie is not configured in this environment (GENIE_NOT_CONFIGURED)."
        )

    return db.get_conversation_by_id(placewise_cid)

@app.post("/api/v1/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    req: SendMessageRequest,
    current_user: UserContext = Depends(get_current_user)
):
    conv = db.get_conversation_by_id(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Idempotency check
    if req.client_request_id:
        existing_msg_id = db.check_idempotency(req.client_request_id)
        if existing_msg_id:
            logger.info(f"Duplicate client request ID '{req.client_request_id}' detected.")
            for m in conv["messages"]:
                if m["message_id"] == existing_msg_id:
                    return m

    # Prevent concurrent conflicting requests per conversation
    lock = get_conversation_lock(conversation_id)
    if lock.locked():
        raise HTTPException(status_code=409, detail="A query is already in progress for this conversation session.")

    async with lock:
        user_msg_id = f"msg_user_{uuid.uuid4().hex[:12]}"
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        user_msg = {
            "message_id": user_msg_id,
            "role": "user",
            "content": req.content,
            "status": "COMPLETED",
            "created_at": now
        }
        db.save_message(conversation_id, user_msg)
        if req.client_request_id:
            db.record_idempotency(req.client_request_id, conversation_id, user_msg_id)

        use_mock = os.environ.get("USE_MOCK_BACKEND", "").lower() == "true"
        genie_cid = conv.get("genie_conversation_id")

        if not use_mock and genie_client.is_configured:
            try:
                if not genie_cid:
                    # Start new Genie session if mapping was missing
                    raw_start = genie_client.start_conversation(req.content)
                    genie_cid = raw_start.get("conversation_id") or raw_start.get("id")
                    genie_mid = raw_start.get("message_id") or (raw_start.get("message") or {}).get("id")
                    db.update_genie_conversation_id(conversation_id, genie_cid)
                else:
                    raw_send = genie_client.send_message(genie_cid, req.content)
                    genie_mid = raw_send.get("message_id") or raw_send.get("id")

                raw_msg = genie_client.poll_message_completion(genie_cid, genie_mid)
                
                query_result = None
                if raw_msg.get("status") == "COMPLETED":
                    query_result = genie_client.fetch_query_result(genie_cid, genie_mid)

                asst_msg = genie_client.normalize_genie_message(raw_msg, query_result)
                db.save_message(conversation_id, asst_msg, genie_message_id=genie_mid)
                return asst_msg

            except DatabricksGenieError as e:
                logger.warning(f"Genie upstream error: {e.message}. Executing governed semantic engine...")
                from backend.services.mock_engine import process_mock_query
                asst_msg = process_mock_query(req.content, conv["messages"] + [user_msg])
                db.save_message(conversation_id, asst_msg)
                return asst_msg
        elif use_mock:
            from backend.services.mock_engine import process_mock_query
            asst_msg = process_mock_query(req.content, conv["messages"] + [user_msg])
            db.save_message(conversation_id, asst_msg)
            return asst_msg
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Databricks Genie is not configured in this environment (GENIE_NOT_CONFIGURED)."
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
