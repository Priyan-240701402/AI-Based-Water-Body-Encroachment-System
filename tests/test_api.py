"""
Complete API Endpoints Coverage Test Suite.
Validates all mandatory REST API endpoints, status codes, and JSON response formats.
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

def test_all_rest_endpoints(client):
    # 1. POST /api/auth/register
    reg = client.post("/api/auth/register", json={
        "name": "API Tester",
        "email": "apitester@example.com",
        "password": "Password123!",
        "role": "citizen"
    })
    assert reg.status_code == 201

    # 2. POST /api/auth/login
    login = client.post("/api/auth/login", json={
        "email": "apitester@example.com",
        "password": "Password123!"
    })
    assert login.status_code == 200

    # 3. GET /api/water-bodies
    wb_list = client.get("/api/water-bodies")
    assert wb_list.status_code == 200
    assert "water_bodies" in wb_list.get_json()

    # 4. GET /api/water-bodies/<id>
    wb_detail = client.get("/api/water-bodies/1")
    assert wb_detail.status_code == 200
    assert wb_detail.get_json()["water_body"]["id"] == 1

    wb_404 = client.get("/api/water-bodies/9999")
    assert wb_404.status_code == 404

    # 5. GET /api/authorities
    auth_list = client.get("/api/authorities")
    assert auth_list.status_code == 200
    assert "authorities" in auth_list.get_json()

    # 6. GET /api/authorities/<id>
    auth_detail = client.get("/api/authorities/1")
    assert auth_detail.status_code == 200

    # 7. POST /api/complaints
    c_create = client.post("/api/complaints", json={
        "title": "API Endpoint Verification Complaint",
        "description": "Verifying full API suite coverage",
        "latitude": 12.9375,
        "longitude": 77.6725,
        "water_body_id": 1,
        "has_construction": True,
        "has_permission": False
    })
    assert c_create.status_code == 201
    c_id = c_create.get_json()["complaint"]["id"]

    # 8. GET /api/complaints
    c_list = client.get("/api/complaints")
    assert c_list.status_code == 200
    assert c_list.get_json()["count"] >= 1

    # Filter query
    c_filter = client.get(f"/api/complaints?water_body_id=1")
    assert c_filter.status_code == 200

    # 9. GET /api/complaints/<id>
    c_get = client.get(f"/api/complaints/{c_id}")
    assert c_get.status_code == 200
    assert c_get.get_json()["complaint"]["id"] == c_id

    c_404 = client.get("/api/complaints/99999")
    assert c_404.status_code == 404

    # 10. PUT /api/complaints/<id>
    c_put = client.put(f"/api/complaints/{c_id}", json={
        "priority": "HIGH"
    })
    assert c_put.status_code == 200
    assert c_put.get_json()["complaint"]["priority"] == "HIGH"

    # 11. POST /api/complaints/<id>/analyze (AI Forward Chaining)
    c_analyze = client.post(f"/api/complaints/{c_id}/analyze")
    assert c_analyze.status_code == 200
    assert c_analyze.get_json()["success"] is True

    # 12. POST /api/complaints/<id>/assign (AI CSP)
    c_assign = client.post(f"/api/complaints/{c_id}/assign")
    assert c_assign.status_code == 200
    assert "assigned_authority" in c_assign.get_json()

    # 13. GET /api/complaints/<id>/inspection-route (AI A* Search)
    c_route = client.get(f"/api/complaints/{c_id}/inspection-route")
    assert c_route.status_code == 200
    assert "route_plan" in c_route.get_json()

    # 14. PUT /api/complaints/<id>/status
    c_status = client.put(f"/api/complaints/{c_id}/status", json={
        "status": "UNDER_VERIFICATION",
        "remarks": "Assigned officer visiting coordinates"
    })
    assert c_status.status_code == 200

    # 15. GET /api/complaints/<id>/history
    c_hist = client.get(f"/api/complaints/{c_id}/history")
    assert c_hist.status_code == 200
    assert len(c_hist.get_json()["history"]) >= 2
