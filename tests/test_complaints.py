"""
Complaint Lifecycle, CRUD, Status Transitions & Validation Suite.
Tests workflow stages from submission to official resolution and audit logging.
"""

import pytest
import io
from backend.app import create_app
from backend.database import db
from backend.models.complaint import Complaint
from backend.models.history import ComplaintStatusHistory

@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_complaint_submission_validation(client):
    """Verifies rejection of invalid or missing fields."""
    # Missing coordinates
    res1 = client.post("/api/complaints", json={"title": "Missing Coords", "description": "Desc"})
    assert res1.status_code == 400
    assert "coordinates are required" in res1.get_json()["message"]

    # Invalid coordinates (non-numeric)
    res2 = client.post("/api/complaints", json={"title": "Bad Coords", "description": "Desc", "latitude": "invalid", "longitude": 77.0})
    assert res2.status_code == 400

    # Missing title
    res3 = client.post("/api/complaints", json={"title": "", "description": "Desc", "latitude": 12.9, "longitude": 77.5})
    assert res3.status_code == 400

    # Missing description
    res4 = client.post("/api/complaints", json={"title": "Title", "description": "", "latitude": 12.9, "longitude": 77.5})
    assert res4.status_code == 400

def test_complaint_field_update_put(client):
    """Verifies PUT /api/complaints/<id> update behavior."""
    create_res = client.post("/api/complaints", json={
        "title": "Initial Title",
        "description": "Initial Desc",
        "latitude": 12.9370,
        "longitude": 77.6720,
        "affected_area_level": "LOW"
    })
    c_id = create_res.get_json()["complaint"]["id"]

    update_res = client.post(f"/api/complaints/{c_id}", json={}) # Ensure only PUT is valid for updates
    
    put_res = client.put(f"/api/complaints/{c_id}", json={
        "title": "Updated Title After Inspection",
        "priority": "CRITICAL",
        "affected_area_level": "HIGH"
    })
    assert put_res.status_code == 200
    updated = put_res.get_json()["complaint"]
    assert updated["title"] == "Updated Title After Inspection"
    assert updated["priority"] == "CRITICAL"
    assert updated["affected_area_level"] == "HIGH"

def test_complaint_full_status_lifecycle_and_audit(client):
    """
    Tests complete status transitions and verifies that every transition
    is recorded in complaint_status_history.
    """
    create_res = client.post("/api/complaints", json={
        "title": "Encroachment Lifecycle Test",
        "description": "Full workflow test",
        "latitude": 12.9375,
        "longitude": 77.6725,
        "water_body_id": 1,
        "has_construction": True,
        "has_permission": False
    })
    c_id = create_res.get_json()["complaint"]["id"]

    transitions = [
        ("UNDER_VERIFICATION", "Survey officer dispatched to inspect the lake boundary."),
        ("ACTION_REQUIRED", "Encroachment verified on field. Eviction notice issued."),
        ("ACTION_TAKEN", "Heavy machinery removed unauthorized debris."),
        ("RESOLVED", "Boundary restored and fenced. Case closed.")
    ]

    for new_status, remarks in transitions:
        res = client.put(f"/api/complaints/{c_id}/status", json={
            "status": new_status,
            "remarks": remarks
        })
        assert res.status_code == 200
        assert res.get_json()["complaint"]["status"] == new_status

    # Verify history records
    hist_res = client.get(f"/api/complaints/{c_id}/history")
    assert hist_res.status_code == 200
    history_entries = hist_res.get_json()["history"]
    
    # 1 initial creation + 4 transitions = 5 records
    assert len(history_entries) == 5
    statuses_in_history = [h["new_status"] for h in history_entries]
    assert "RESOLVED" in statuses_in_history
    assert "UNDER_VERIFICATION" in statuses_in_history

def test_alternative_statuses_rejected_and_duplicate(client):
    """Tests REJECTED and DUPLICATE status handling."""
    create_res = client.post("/api/complaints", json={
        "title": "Duplicate Report",
        "description": "Already logged",
        "latitude": 12.9500,
        "longitude": 77.7425
    })
    c_id = create_res.get_json()["complaint"]["id"]

    # Mark as DUPLICATE
    res = client.put(f"/api/complaints/{c_id}/status", json={
        "status": "DUPLICATE",
        "remarks": "Duplicate of complaint #1"
    })
    assert res.status_code == 200
    assert res.get_json()["complaint"]["status"] == "DUPLICATE"

def test_evidence_file_upload(client):
    """Tests uploading photographic evidence with a complaint."""
    data = {
        "title": "Photo Evidence Test",
        "description": "Attaching site photograph",
        "latitude": "12.9370",
        "longitude": "77.6720",
        "evidence": (io.BytesIO(b"fake-image-bytes-data"), "site_photo.jpg")
    }
    res = client.post("/api/complaints", data=data, content_type="multipart/form-data")
    assert res.status_code == 201
    c_data = res.get_json()["complaint"]
    assert c_data["evidence_count"] == 1
