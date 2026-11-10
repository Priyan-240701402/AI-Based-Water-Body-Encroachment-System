"""
Authorization and Role-Based Access Control Tests.
Validates role separation between Citizen, Authority, and Admin roles.
"""

import pytest
from backend.app import create_app
from backend.database import db
from backend.models.user import User

@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_unauthenticated_protected_views(client):
    # Attempting to access citizen dashboard without login should redirect
    res = client.get("/citizen/dashboard")
    assert res.status_code == 302
    assert "/login" in res.location

    # Admin dashboard without login should redirect
    res_admin = client.get("/admin/dashboard")
    assert res_admin.status_code == 302
    assert "/login" in res_admin.location

def test_citizen_role_isolation(client):
    # Login as citizen
    client.post("/api/auth/login", json={
        "email": "citizen@example.com",
        "password": "Password@123"
    })

    # Citizen accessing citizen dashboard should be allowed
    res_cit = client.get("/citizen/dashboard")
    assert res_cit.status_code == 200

    # Verify citizen profile indicates citizen role
    res_me = client.get("/api/auth/me")
    assert res_me.get_json()["user"]["role"] == "citizen"

def test_authority_role_access(client):
    # Login as authority officer
    client.post("/api/auth/login", json={
        "email": "officer.revenue@waterbodies.gov.in",
        "password": "Password@123"
    })

    res_admin = client.get("/admin/dashboard")
    assert res_admin.status_code == 200

    res_map = client.get("/admin/map")
    assert res_map.status_code == 200
