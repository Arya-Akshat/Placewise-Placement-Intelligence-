import pytest
from backend.services.databricks_genie import DatabricksGenieClient, DatabricksGenieError

def test_genie_client_not_configured_by_default():
    client = DatabricksGenieClient(host="", token="", space_id="")
    assert client.is_configured is False

def test_genie_message_normalization_table_and_kpi():
    client = DatabricksGenieClient(host="https://fake.databricks.com", token="dapifake", space_id="0123456789ab")
    
    raw_msg = {
        "id": "msg_001",
        "status": "COMPLETED",
        "content": "Placement rate for CSE in 2024 is 51.49%."
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
    assert norm["message_id"] == "msg_001"
    assert norm["status"] == "COMPLETED"
    assert norm["attachment"] is not None
    assert norm["attachment"]["recommended_visualization"] == "KPI"
    assert len(norm["attachment"]["kpis"]) == 1
    assert norm["attachment"]["kpis"][0]["value"] == "51.49%"

def test_genie_message_normalization_large_result_truncation():
    client = DatabricksGenieClient(host="https://fake.databricks.com", token="dapifake", space_id="0123456789ab", max_result_rows=5)
    
    raw_msg = {"id": "msg_002", "status": "COMPLETED", "content": "Sample matches"}
    query_result = {
        "manifest": {
            "schema": {"columns": [{"name": "id", "type_text": "INT"}]},
            "total_row_count": 20
        },
        "result": {
            "data_array": [[i] for i in range(20)]
        }
    }
    norm = client.normalize_genie_message(raw_msg, query_result)
    table = norm["attachment"]["table_data"]
    assert table["total_row_count"] == 20
    assert table["truncated"] is True
    assert len(table["rows"]) == 5

def test_genie_message_normalization_clarification():
    client = DatabricksGenieClient(host="https://fake.databricks.com", token="dapifake", space_id="0123456789ab")
    raw_msg = {
        "id": "msg_003",
        "status": "CLARIFICATION_REQUIRED",
        "content": "Which metric would you like to rank companies by?",
        "clarification": {
            "prompt": "Select a metric:",
            "options": ["Placements Count", "Average Package", "Conversion Rate"]
        }
    }
    norm = client.normalize_genie_message(raw_msg)
    assert norm["status"] == "CLARIFICATION_REQUIRED"
    assert norm["clarification"] is not None
    assert len(norm["clarification"]["options"]) == 3
