"""
Role-Based Portals and Access Control Test Suite.
Validates isolated portals, navigation routes, and RBAC enforcement for Citizen, Officer, and Admin.
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

def test_login_role_redirection(client):
    # Citizen Login -> /citizen/dashboard
    res_cit = client.post("/api/auth/login", json={
        "email": "citizen@example.com",
        "password": "Password@123"
    })
    assert res_cit.status_code == 200
    assert res_cit.get_json()["redirect_url"] == "/citizen/dashboard"

    client.get("/api/auth/logout")

    # Officer Login -> /officer/dashboard
    res_off = client.post("/api/auth/login", json={
        "email": "officer.revenue@waterbodies.gov.in",
        "password": "Password@123"
    })
    assert res_off.status_code == 200
    assert res_off.get_json()["redirect_url"] == "/officer/dashboard"

    client.get("/api/auth/logout")

    # Admin Login -> /admin/dashboard
    res_adm = client.post("/api/auth/login", json={
        "email": "admin@waterbodies.gov.in",
        "password": "Password@123"
    })
    assert res_adm.status_code == 200
    assert res_adm.get_json()["redirect_url"] == "/admin/dashboard"

def test_citizen_portal_access(client):
    client.post("/api/auth/login", json={
        "email": "citizen@example.com",
        "password": "Password@123"
    })

    # Citizen accessing Citizen Portal pages
    assert client.get("/citizen/dashboard").status_code == 200
    assert client.get("/citizen/complaints/new").status_code == 200
    assert client.get("/citizen/complaints").status_code == 200
    assert client.get("/citizen/profile").status_code == 200

    # Citizen blocked from Admin Management pages -> 403 / Access Denied
    assert client.get("/admin/users").status_code == 403
    assert client.get("/admin/officers").status_code == 403
    assert client.get("/admin/authorities").status_code == 403
    assert client.get("/admin/ai-rules").status_code == 403

def test_officer_portal_access(client):
    client.post("/api/auth/login", json={
        "email": "officer.revenue@waterbodies.gov.in",
        "password": "Password@123"
    })

    # Officer accessing Officer Portal pages
    assert client.get("/officer/dashboard").status_code == 200
    assert client.get("/officer/complaints").status_code == 200
    assert client.get("/officer/map").status_code == 200
    assert client.get("/officer/inspections").status_code == 200
    assert client.get("/officer/profile").status_code == 200

    # Officer blocked from Admin Management pages
    assert client.get("/admin/users").status_code == 403
    assert client.get("/admin/officers").status_code == 403

def test_admin_portal_access(client):
    client.post("/api/auth/login", json={
        "email": "admin@waterbodies.gov.in",
        "password": "Password@123"
    })

    # Admin accessing Admin Portal pages
    assert client.get("/admin/dashboard").status_code == 200
    assert client.get("/admin/users").status_code == 200
    assert client.get("/admin/officers").status_code == 200
    assert client.get("/admin/authorities").status_code == 200
    assert client.get("/admin/water-bodies").status_code == 200
    assert client.get("/admin/assignments").status_code == 200
    assert client.get("/admin/reports").status_code == 200
    assert client.get("/admin/ai-rules").status_code == 200
    assert client.get("/admin/audit-logs").status_code == 200
