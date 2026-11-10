"""
Integration tests for Flask Authentication and Complaint REST APIs.
"""

import pytest
import json
from backend.app import create_app
from backend.database import db

@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_api_auth_and_complaint_flow(client):
    # 1. Register a test citizen
    reg_res = client.post("/api/auth/register", json={
        "name": "Test Citizen",
        "email": "testcitizen@example.com",
        "password": "Password123!",
        "role": "citizen"
    })
    assert reg_res.status_code == 201
    assert reg_res.get_json()["success"] is True

    # 2. Login
    login_res = client.post("/api/auth/login", json={
        "email": "testcitizen@example.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200

    # 3. Submit Complaint
    complaint_res = client.post("/api/complaints", json={
        "title": "Illegal Landfilling in Demo Lake",
        "description": "Earthmovers dumping debris inside the north embankment.",
        "latitude": 12.9370,
        "longitude": 77.6720,
        "water_body_id": 1,
        "has_construction": True,
        "has_permission": False,
        "affected_area_level": "HIGH"
    })
    assert complaint_res.status_code == 201
    complaint_data = complaint_res.get_json()["complaint"]
    assert complaint_data["status"] in ("AI_REVIEWED", "ASSIGNED")
    assert "Official Verification" in complaint_data["classification"]
    assert complaint_data["priority"] == "HIGH"
    complaint_id = complaint_data["id"]

    # 4. Trigger AI Analyze endpoint
    ai_res = client.post(f"/api/complaints/{complaint_id}/analyze")
    assert ai_res.status_code == 200
    assert "forward_chaining" in ai_res.get_json()["result"] or "reasoning_trace" in ai_res.get_json()["result"]

    # 5. Trigger Backward Chaining endpoint
    bc_res = client.post(f"/api/complaints/{complaint_id}/verify-backward", json={
        "goal": "REQUIRES_OFFICIAL_VERIFICATION"
    })
    assert bc_res.status_code == 200
    assert bc_res.get_json()["proof"]["proven"] is True

    # 6. Retrieve history
    hist_res = client.get(f"/api/complaints/{complaint_id}/history")
    assert hist_res.status_code == 200
    assert len(hist_res.get_json()["history"]) >= 1

def test_web_templates_render(client):
    """Test that all public and dashboard views render without template syntax errors."""
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert b"JalRaksha" in res_home.data

    res_login = client.get("/login")
    assert res_login.status_code == 200
    assert b"Sign In" in res_login.data

    res_reg = client.get("/register")
    assert res_reg.status_code == 200
    assert b"Create Account" in res_reg.data

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Admin"
        sess["role"] = "authority"

    res_map = client.get("/admin/map")
    assert res_map.status_code == 200
    assert b"GIS Water Body" in res_map.data

