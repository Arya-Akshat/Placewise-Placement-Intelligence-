# Placewise Backend REST API Contract (v1)

**Base URL:** `http://localhost:8000` (Configured via `VITE_API_BASE_URL`)  
**Format:** JSON over HTTPS/HTTP  

---

## 1. Endpoints

### `POST /api/v1/conversations`
Creates a new conversation session and optionally processes the initial message.

* **Request**:
  ```json
  {
    "content": "What is the placement rate for CSE in 2024?",
    "client_request_id": "req_1725200000"
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "conversation_id": "conv_a8b9c1d2e3f4",
    "title": "What is the placement rate for",
    "created_at": "2026-09-01T19:24:00Z",
    "updated_at": "2026-09-01T19:24:00Z",
    "messages": [ ... ]
  }
  ```

### `POST /api/v1/conversations/{conversation_id}/messages`
Appends a user message and returns the structured assistant intelligence response.

* **Request**:
  ```json
  {
    "content": "How does that compare with ECE?",
    "client_request_id": "req_1725200001"
  }
  ```

### `GET /api/v1/conversations/{conversation_id}`
Returns all messages for the specified conversation session.

### `GET /api/v1/conversations`
Returns a list of recent conversation summaries for the sidebar history.

### `GET /api/v1/health`
Health check and database mirror status.
