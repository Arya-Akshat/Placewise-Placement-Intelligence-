import pytest
from backend.services.databricks_genie import DatabricksGenieClient

def test_genie_client_not_configured_by_default():
    client = DatabricksGenieClient(host="", token="", space_id="")
    assert client.is_configured is False

def test_genie_message_normalization_table_and_kpi():
    client = DatabricksGenieClient()
    raw_msg = {
        "id": "msg_test_01",
        "content": "CSE 2024 placement rate was 51.49%.",
        "status": "COMPLETED",
        "attachments": [
            {
                "type": "QUERY",
                "query": {
                    "id": "qry_01",
                    "text": "SELECT department_code, placement_rate FROM semantic.genie_department_performance WHERE department_code = 'CSE';"
                }
            }
        ]
    }
    query_result = {
        "manifest": {
            "schema": {
                "columns": [
                    {"name": "department_code", "type_text": "STRING"},
                    {"name": "placement_rate", "type_text": "DOUBLE"}
                ]
            },
            "total_row_count": 1
        },
        "result": {
            "data_array": [["CSE", 51.49]]
        }
    }

    norm = client.normalize_genie_message(raw_msg, query_result)
    assert norm["status"] == "COMPLETED"
    assert norm["content"] == "CSE 2024 placement rate was 51.49%."
    assert norm["attachment"] is not None
    assert norm["attachment"]["recommended_visualization"] == "KPI"
    assert norm["attachment"]["table_data"]["total_row_count"] == 1
    assert norm["attachment"]["table_data"]["rows"][0]["placement_rate"] == 51.49
    assert norm["attachment"]["table_data"]["rows"][0]["department_code"] == "CSE"

def test_genie_message_normalization_large_result_truncation():
    client = DatabricksGenieClient(max_result_rows=5)
    raw_msg = {"id": "msg_02", "content": "Sample query", "status": "COMPLETED"}
    query_result = {
        "manifest": {
            "schema": {"columns": [{"name": "id", "type_text": "INT"}]},
            "total_row_count": 125002500
        },
        "result": {
            "data_array": [[i] for i in range(20)]
        }
    }
    norm = client.normalize_genie_message(raw_msg, query_result)
    table = norm["attachment"]["table_data"]
    assert table["total_row_count"] == 125002500
    assert table["truncated"] is True
    assert len(table["rows"]) == 5

def test_genie_message_normalization_clarification():
    client = DatabricksGenieClient()
    raw_msg = {
        "id": "msg_03",
        "content": "Which batch would you like to analyze?",
        "status": "CLARIFICATION_REQUIRED",
        "options": ["2024 Batch", "2023 Batch", "2025 Batch"]
    }
    norm = client.normalize_genie_message(raw_msg)
    assert norm["status"] == "CLARIFICATION_REQUIRED"
    assert norm["clarification"] is not None
    assert len(norm["clarification"]["options"]) == 3
