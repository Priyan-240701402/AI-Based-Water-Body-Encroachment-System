"""
End-to-End User & Authority Scenarios (Requirement 12).
Tests complete user journeys from submission through reasoning, CSP, and resolution.
"""

import pytest
from backend.app import create_app
from backend.database import db

@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_scenario_1_valid_complaint_full_cycle(client):
    """
    Scenario 1:
    Citizen registers -> Logs in -> Submits valid complaint
    -> AI analyzes -> Forward Chaining deduces Possible Encroachment
    -> CSP assigns Authority -> Authority surveys and resolves
    -> Citizen views RESOLVED outcome.
    """
    # 1. Citizen registers & logs in
    client.post("/api/auth/register", json={
        "name": "Citizen Ramesh",
        "email": "ramesh@example.com",
        "password": "Password123!",
        "role": "citizen"
    })
    client.post("/api/auth/login", json={
        "email": "ramesh@example.com",
        "password": "Password123!"
    })

    # 2. Citizen submits complaint
    sub_res = client.post("/api/complaints", json={
        "title": "Earth dumping on Bellandur Lake shore",
        "description": "Trucks dumping soil into lake buffer zone",
        "latitude": 12.9375,
        "longitude": 77.6725,
        "water_body_id": 1,
        "has_construction": True,
        "has_permission": False,
        "affected_area_level": "HIGH"
    })
    assert sub_res.status_code == 201
    c_id = sub_res.get_json()["complaint"]["id"]

    # 3. Check AI Forward Chaining analysis
    c_data = sub_res.get_json()["complaint"]
    assert "Verification" in c_data["classification"]
    assert c_data["priority"] == "HIGH"
    assert c_data["status"] == "ASSIGNED"
    assert c_data["current_assigned_authority"] is not None

    # 4. Authority officer logs in and updates status
    client.post("/api/auth/login", json={
        "email": "officer.revenue@waterbodies.gov.in",
        "password": "Password@123"
    })

    # Transition to UNDER_VERIFICATION
    client.put(f"/api/complaints/{c_id}/status", json={
        "status": "UNDER_VERIFICATION",
        "remarks": "Officer inspecting revenue survey boundaries."
    })

    # Transition to ACTION_TAKEN
    client.put(f"/api/complaints/{c_id}/status", json={
        "status": "ACTION_TAKEN",
        "remarks": "Earthmovers evicted and dumped soil removed."
    })

    # Transition to RESOLVED
    res_resolve = client.put(f"/api/complaints/{c_id}/status", json={
        "status": "RESOLVED",
        "remarks": "Restoration complete. Boundary trench excavated."
    })
    assert res_resolve.status_code == 200

    # 5. Citizen re-authenticates and verifies RESOLVED status in history
    client.post("/api/auth/login", json={
        "email": "ramesh@example.com",
        "password": "Password123!"
    })
    view_res = client.get(f"/api/complaints/{c_id}")
    assert view_res.status_code == 200
    final_complaint = view_res.get_json()["complaint"]
    assert final_complaint["status"] == "RESOLVED"
    assert len(final_complaint["status_history"]) >= 4

def test_scenario_2_insufficient_information(client):
    """
    Scenario 2:
    Citizen submits report with no active construction and outside boundary
    -> AI Forward Chaining determines Insufficient Information / No Indicator
    -> Case logged safely for administrative review.
    """
    client.post("/api/auth/login", json={"email": "citizen@example.com", "password": "Password@123"})

    res = client.post("/api/complaints", json={
        "title": "Vague report about distant lake",
        "description": "Saw someone walking near water",
        "latitude": 13.5000, # Far outside known lake boundary
        "longitude": 78.5000,
        "has_construction": False,
        "has_permission": False,
        "affected_area_level": "LOW"
    })
    assert res.status_code == 201
    c = res.get_json()["complaint"]
    assert c["classification"] in ("No Preliminary Encroachment Indicator", "Insufficient Information")

def test_scenario_3_no_preliminary_indicator(client):
    """
    Scenario 3:
    Report filed where construction is false and coordinates outside boundary.
    -> Forward Chaining does NOT infer Possible Encroachment.
    """
    client.post("/api/auth/login", json={"email": "citizen@example.com", "password": "Password@123"})
    res = client.post("/api/complaints", json={
        "title": "Clean water body check",
        "description": "Routine observation, no physical construction",
        "latitude": 12.0000,
        "longitude": 77.0000,
        "has_construction": False,
        "has_permission": False
    })
    assert res.status_code == 201
    c = res.get_json()["complaint"]
    assert c["classification"] == "No Preliminary Encroachment Indicator"
    assert c["priority"] == "LOW"

def test_scenario_4_authority_assignment_graceful_handling(client):
    """
    Scenario 4:
    Complaint in a remote or unserviced district where no authority is eligible.
    -> System handles gracefully without assigning incorrect agency.
    """
    from backend.ai.csp import AuthorityCSP
    
    # Empty authority domain
    csp = AuthorityCSP([])
    result = csp.solve({"water_body_type": "LAKE", "district": "Unknown Remote District"})
    
    assert result["success"] is False
    assert result["assigned_authority"] is None
    assert "No active authority satisfied" in result["assignment_reason"]
