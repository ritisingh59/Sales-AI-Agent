"""
FastAPI Endpoint Integration Tests using TestClient.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200

def test_scenarios_endpoint():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) >= 5
    assert scenarios[0]["tag"] == "Multilingual"

def test_chat_and_analytics_flow():
    session_id = "test-e2e-session"
    
    # 1. User sends message
    chat_resp = client.post("/api/chat", json={
        "session_id": session_id,
        "message": "Namaste! 3 BHK price kitna hai aur kya Saturday 11 AM site visit ho sakta hai?"
    })
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert data["tool_executed"] is True
    
    # 2. End session and extract analytics
    end_resp = client.post("/api/end-session", json={"session_id": session_id})
    assert end_resp.status_code == 200
    analytics_data = end_resp.json()
    assert analytics_data["status"] == "completed"
    assert "analytics" in analytics_data
    assert analytics_data["analytics"]["preferred_configuration"] == "3 BHK"
    assert analytics_data["analytics"]["site_visit_status"] == "Confirmed"
    
    # 3. Reset session
    reset_resp = client.post("/api/reset", json={"session_id": session_id})
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "reset_successful"
