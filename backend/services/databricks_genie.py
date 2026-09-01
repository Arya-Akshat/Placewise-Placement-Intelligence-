"""
PLACEWISE — Production Databricks Genie Client
==============================================
Manages Databricks Genie space conversations, asynchronous message polling,
query result retrieval, error classification, and response normalization.
"""

import os, sys, time, json, random, logging
from typing import Dict, Any, Optional, Tuple, List
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

logger = logging.getLogger("DatabricksGenieClient")

class DatabricksGenieError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{code}] {message} (HTTP {status_code})")

class DatabricksGenieClient:
    def __init__(
        self,
        host: Optional[str] = None,
        token: Optional[str] = None,
        space_id: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        agent_timeout_seconds: Optional[int] = None,
        poll_interval: Optional[float] = None,
        max_result_rows: Optional[int] = None
    ):
        self.host = (host if host is not None else os.environ.get("DATABRICKS_HOST", "")).strip().rstrip("/")
        self.token = (token if token is not None else os.environ.get("DATABRICKS_TOKEN", "")).strip()
        self.space_id = (space_id if space_id is not None else os.environ.get("DATABRICKS_GENIE_SPACE_ID", "")).strip()
        
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else int(os.environ.get("GENIE_TIMEOUT_SECONDS", 60))
        self.agent_timeout_seconds = agent_timeout_seconds if agent_timeout_seconds is not None else int(os.environ.get("GENIE_AGENT_TIMEOUT_SECONDS", 120))
        self.poll_interval = poll_interval if poll_interval is not None else float(os.environ.get("GENIE_POLL_INTERVAL_SECONDS", 1.0))
        self.max_result_rows = max_result_rows if max_result_rows is not None else int(os.environ.get("GENIE_MAX_RESULT_ROWS", 10000))

    @property
    def is_configured(self) -> bool:
        return bool(
            self.host
            and self.token
            and self.space_id
            and not self.host.startswith("https://<")
            and not self.token.startswith("dapi...")
            and len(self.space_id) >= 10
        )

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "Placewise-Genie-Client/2.0"
        }

    def _map_http_error(self, response: requests.Response) -> DatabricksGenieError:
        status = response.status_code
        try:
            body = response.json()
            msg = body.get("message") or body.get("error") or response.text
        except Exception:
            msg = response.text or "Unknown upstream error"

        if status == 401:
            return DatabricksGenieError("AUTHENTICATION_ERROR", "Invalid or expired Databricks token.", 401)
        elif status == 403:
            return DatabricksGenieError("AUTHORIZATION_ERROR", "Insufficient permissions on target Genie Space or SQL Warehouse.", 403)
        elif status == 404:
            return DatabricksGenieError("GENIE_NOT_FOUND", f"Genie Space '{self.space_id}' not found.", 404)
        elif status == 429:
            return DatabricksGenieError("GENIE_RATE_LIMIT", "Genie rate limit exceeded. Please wait a moment.", 429)
        elif status in (408, 504):
            return DatabricksGenieError("GENIE_TIMEOUT", "Genie query execution timed out.", 504)
        elif status in (500, 502, 503):
            return DatabricksGenieError("GENIE_UNAVAILABLE", "Databricks Genie service is temporarily unavailable.", 503)
        else:
            return DatabricksGenieError("INTERNAL_ERROR", f"Genie API error: {msg}", status)

    def _request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        max_retries = 3
        backoff = 1.0

        for attempt in range(max_retries):
            try:
                resp = requests.request(method, url, headers=self._get_headers(), timeout=20, **kwargs)
                if resp.status_code == 429 or (resp.status_code >= 500 and attempt < max_retries - 1):
                    sleep_time = backoff + random.uniform(0.1, 0.5)
                    logger.warning(f"Genie API returned {resp.status_code}. Retrying in {sleep_time:.2f}s (Attempt {attempt+1}/{max_retries})...")
                    time.sleep(sleep_time)
                    backoff *= 2.0
                    continue

                if not resp.ok:
                    raise self._map_http_error(resp)

                return resp
            except requests.exceptions.Timeout:
                if attempt == max_retries - 1:
                    raise DatabricksGenieError("GENIE_TIMEOUT", "Connection to Databricks Genie timed out.", 504)
                time.sleep(backoff)
                backoff *= 2.0
            except requests.exceptions.ConnectionError as e:
                if attempt == max_retries - 1:
                    raise DatabricksGenieError("GENIE_UNAVAILABLE", f"Cannot connect to Databricks host: {str(e)}", 503)
                time.sleep(backoff)
                backoff *= 2.0

        raise DatabricksGenieError("GENIE_UNAVAILABLE", "Failed to connect to Genie after maximum retries.", 503)

    def check_ready(self) -> Tuple[bool, str]:
        if not self.is_configured:
            return False, "DATABRICKS_HOST, DATABRICKS_TOKEN, or DATABRICKS_GENIE_SPACE_ID not configured."
        try:
            url = f"{self.host}/api/2.0/genie/spaces/{self.space_id}"
            resp = self._request_with_retry("GET", url)
            return True, "Databricks Genie Space reachable."
        except Exception as e:
            return False, str(e)

    def start_conversation(self, content: str) -> Dict[str, Any]:
        if not self.is_configured:
            raise DatabricksGenieError("GENIE_NOT_CONFIGURED", "Databricks Genie credentials are not configured.", 503)
        url = f"{self.host}/api/2.0/genie/spaces/{self.space_id}/start-conversation"
        payload = {"content": content}
        resp = self._request_with_retry("POST", url, json=payload)
        return resp.json()

    def send_message(self, conversation_id: str, content: str) -> Dict[str, Any]:
        if not self.is_configured:
            raise DatabricksGenieError("GENIE_NOT_CONFIGURED", "Databricks Genie credentials are not configured.", 503)
        url = f"{self.host}/api/2.0/genie/spaces/{self.space_id}/conversations/{conversation_id}/messages"
        payload = {"content": content}
        resp = self._request_with_retry("POST", url, json=payload)
        return resp.json()

    def get_message(self, conversation_id: str, message_id: str) -> Dict[str, Any]:
        url = f"{self.host}/api/2.0/genie/spaces/{self.space_id}/conversations/{conversation_id}/messages/{message_id}"
        resp = self._request_with_retry("GET", url)
        return resp.json()

    def poll_message_completion(self, conversation_id: str, message_id: str, is_agent_mode: bool = False) -> Dict[str, Any]:
        max_duration = self.agent_timeout_seconds if is_agent_mode else self.timeout_seconds
        start_time = time.time()

        while (time.time() - start_time) < max_duration:
            msg_data = self.get_message(conversation_id, message_id)
            status = msg_data.get("status", "").upper()

            if status in ("COMPLETED", "FAILED", "CANCELED", "CLARIFICATION_REQUIRED"):
                return msg_data

            time.sleep(self.poll_interval)

        raise DatabricksGenieError("GENIE_TIMEOUT", f"Genie query execution exceeded {max_duration} seconds timeout.", 504)

    def fetch_query_result(self, conversation_id: str, message_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.host}/api/2.0/genie/spaces/{self.space_id}/conversations/{conversation_id}/messages/{message_id}/query-result"
        try:
            resp = self._request_with_retry("GET", url)
            return resp.json()
        except DatabricksGenieError as e:
            if e.status_code == 404:
                return None
            raise e

    def column_to_display_name(self, col: str) -> str:
        mapping = {
            "department_code": "Department",
            "department_name": "Department Name",
            "graduation_year": "Graduation Batch",
            "total_students": "Total Students",
            "eligible_students": "Eligible Students",
            "placed_students": "Placed Students",
            "placement_rate": "Placement Rate",
            "average_ctc_lpa": "Average CTC (LPA)",
            "median_ctc_lpa": "Median CTC (LPA)",
            "highest_ctc_lpa": "Highest CTC (LPA)",
            "placement_rate_yoy": "Prev Year Rate",
            "placement_rate_change_points": "YoY Change (pp)",
            "company_name": "Company",
            "industry": "Industry",
            "company_type": "Company Type",
            "placements_count": "Placements",
            "openings_count": "Openings",
            "applications_count": "Applications",
            "interviews_count": "Interviews",
            "offers_count": "Offers",
            "interview_to_offer_rate": "Interview Conversion %",
            "skill_name": "Skill / Technology",
            "skill_category": "Category",
            "demand_rank": "Demand Rank",
            "job_posting_count": "Job Postings",
            "student_supply_ratio": "Student Supply %",
            "market_demand_ratio": "Market Demand %",
            "skill_supply_demand_gap": "Supply-Demand Gap",
            "student_id": "Student ID",
            "full_name": "Candidate Name",
            "cgpa": "CGPA",
            "academic_score": "Academic Score",
            "skill_score": "Skill Score",
            "interview_score": "Interview Score",
            "placement_readiness_score": "Readiness Score",
            "readiness_band": "Readiness Band",
            "placement_status": "Status",
            "candidate_fit_band": "Candidate Fit",
            "skill_match_percentage": "Skill Match %",
            "skill_gap_percentage": "Skill Gap %",
            "missing_mandatory_skill_count": "Missing Mandatory Skills"
        }
        return mapping.get(col, col.replace("_", " ").title())

    def normalize_genie_message(
        self,
        raw_msg: Dict[str, Any],
        query_result: Optional[Dict[str, Any]] = None,
        custom_msg_id: Optional[str] = None
    ) -> Dict[str, Any]:
        msg_id = custom_msg_id or raw_msg.get("message_id") or raw_msg.get("id") or f"msg_{int(time.time()*1000)}"
        status = raw_msg.get("status", "COMPLETED").upper()
        
        # Extract assistant text answer
        content = raw_msg.get("content") or raw_msg.get("text") or ""
        attachments = raw_msg.get("attachments") or []
        for a in attachments:
            text_obj = a.get("text")
            if text_obj and text_obj.get("purpose") == "TEXT_ATTACHMENT_PURPOSE_ANSWER":
                content = text_obj.get("content", content)
                break

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Check for clarification request
        clarification_payload = None
        if "clarification" in raw_msg or status == "CLARIFICATION_REQUIRED" or "options" in raw_msg:
            opts = []
            raw_opts = raw_msg.get("clarification", {}).get("options") or raw_msg.get("options") or []
            for i, o in enumerate(raw_opts):
                if isinstance(o, str):
                    opts.append({"id": f"opt_{i+1}", "label": o, "value": o})
                elif isinstance(o, dict):
                    opts.append({
                        "id": o.get("id", f"opt_{i+1}"),
                        "label": o.get("label", o.get("text", "")),
                        "value": o.get("value", o.get("label", ""))
                    })
            clarification_payload = {
                "prompt": raw_msg.get("clarification", {}).get("prompt") or content or "Please select an option:",
                "options": opts
            }
            status = "CLARIFICATION_REQUIRED"

        # Check for Agent Mode multi-step analysis
        agent_analysis = None
        if "agent_analysis" in raw_msg or "analysis" in raw_msg:
            raw_analysis = raw_msg.get("agent_analysis") or raw_msg.get("analysis")
            if isinstance(raw_analysis, dict):
                agent_analysis = {
                    "summary": raw_analysis.get("summary", content),
                    "findings": raw_analysis.get("findings", []),
                    "evidence": raw_analysis.get("evidence", []),
                    "supporting_chart_type": raw_analysis.get("supporting_chart_type", "BAR")
                }

        # Check for Query attachments
        attachment_payload = None
        query_att = None
        for a in attachments:
            if a.get("type") == "QUERY" or "query" in a:
                query_att = a.get("query") or a
                break

        if query_att or query_result:
            q_id = (query_att or {}).get("query_id") or (query_att or {}).get("id") or f"qry_{int(time.time()*1000)}"
            q_text = (query_att or {}).get("query_text") or (query_att or {}).get("text") or ""
            source_obj = (query_att or {}).get("source_object") or "placewise.semantic"

            table_data = None
            kpis = []
            rec_vis = "TABLE"

            if query_result and "manifest" in query_result and "result" in query_result:
                manifest_cols = query_result["manifest"]["schema"]["columns"]
                raw_data_array = query_result["result"].get("data_array", [])
                total_rows = query_result["manifest"].get("total_row_count", len(raw_data_array))

                bounded_data = raw_data_array[:self.max_result_rows]
                is_truncated = total_rows > len(bounded_data)

                col_defs = []
                for c in manifest_cols:
                    cname = c.get("name") or c.get("column_name")
                    col_defs.append({
                        "name": cname,
                        "type_text": c.get("type_text") or c.get("type_name") or "STRING",
                        "display_name": self.column_to_display_name(cname)
                    })

                rows = []
                for row_vals in bounded_data:
                    row_dict = {}
                    for col_idx, col_def in enumerate(col_defs):
                        val = row_vals[col_idx] if col_idx < len(row_vals) else None
                        row_dict[col_def["name"]] = val
                    rows.append(row_dict)

                table_data = {
                    "columns": col_defs,
                    "rows": rows,
                    "total_row_count": total_rows,
                    "truncated": is_truncated
                }

                col_names = [c["name"] for c in col_defs]
                if len(rows) == 1:
                    r0 = rows[0]
                    rec_vis = "KPI"
                    if "placement_rate" in r0:
                        kpis.append({"label": "Placement Rate", "value": f"{r0['placement_rate']}%"})
                    if "placed_students" in r0:
                        kpis.append({"label": "Placed Students", "value": f"{r0['placed_students']:,}"})
                    if "eligible_students" in r0:
                        kpis.append({"label": "Eligible Students", "value": f"{r0['eligible_students']:,}"})
                    if "average_ctc_lpa" in r0:
                        kpis.append({"label": "Average CTC", "value": f"₹{r0['average_ctc_lpa']} LPA"})
                elif any(x in col_names for x in ["placement_rate", "placements_count", "job_posting_count", "placement_rate_change_points"]):
                    rec_vis = "BAR"
                elif any(x in col_names for x in ["graduation_year", "admission_year"]):
                    rec_vis = "LINE"

            attachment_payload = {
                "query_id": q_id,
                "query_text": q_text,
                "source_object": source_obj,
                "table_data": table_data,
                "recommended_visualization": rec_vis,
                "kpis": kpis if kpis else None
            }

        # Follow up suggestions
        suggestions = []
        for a in attachments:
            sq = a.get("suggested_questions")
            if sq and "questions" in sq:
                suggestions.extend(sq["questions"])

        return {
            "message_id": msg_id,
            "role": "assistant",
            "content": content,
            "status": status,
            "created_at": now,
            "attachment": attachment_payload,
            "clarification": clarification_payload,
            "agent_analysis": agent_analysis,
            "follow_up_suggestions": suggestions if suggestions else raw_msg.get("follow_up_suggestions")
        }
