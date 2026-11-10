"""
Authentication & User Lifecycle Tests.
Tests registration, login, logout, password hashing, and session persistence.
"""

import pytest
from backend.app import create_app
from backend.database import db
from backend.models.user import User
from backend.utils.auth_helpers import verify_password

@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_valid_registration(client):
    res = client.post("/api/auth/register", json={
        "name": "Anil Verma",
        "email": "anil.verma@example.com",
        "password": "SecurePassword123!",
        "role": "citizen",
        "phone": "+91-9876543200"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["email"] == "anil.verma@example.com"
    assert data["user"]["role"] == "citizen"

def test_duplicate_registration_rejected(client):
    payload = {
        "name": "Duplicate User",
        "email": "dup@example.com",
        "password": "Password123!",
        "role": "citizen"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.get_json()["message"]

def test_registration_validation_rules(client):
    # Missing email
    res1 = client.post("/api/auth/register", json={"name": "No Email", "password": "pass"})
    assert res1.status_code == 400

    # Password too short (< 6 chars)
    res2 = client.post("/api/auth/register", json={"name": "Short", "email": "short@example.com", "password": "123"})
    assert res2.status_code == 400

def test_login_flow(client):
    client.post("/api/auth/register", json={
        "name": "Login Tester",
        "email": "login_tester@example.com",
        "password": "ValidPassword999",
        "role": "citizen"
    })

    # Valid Login
    res_valid = client.post("/api/auth/login", json={
        "email": "login_tester@example.com",
        "password": "ValidPassword999"
    })
    assert res_valid.status_code == 200
    assert res_valid.get_json()["success"] is True

    # Invalid Password
    res_bad_pw = client.post("/api/auth/login", json={
        "email": "login_tester@example.com",
        "password": "WrongPassword!"
    })
    assert res_bad_pw.status_code == 401

    # Non-existent User
    res_no_user = client.post("/api/auth/login", json={
        "email": "ghost_user@example.com",
        "password": "AnyPassword"
    })
    assert res_no_user.status_code == 401

def test_password_hashing_security(client):
    client.post("/api/auth/register", json={
        "name": "Hash Check",
        "email": "hash_check@example.com",
        "password": "PlainTextSecret123"
    })
    user = User.query.filter_by(email="hash_check@example.com").first()
    assert user is not None
    # Must NOT equal plain text
    assert user.password_hash != "PlainTextSecret123"
    assert verify_password(user.password_hash, "PlainTextSecret123") is True
    assert verify_password(user.password_hash, "WrongSecret") is False

def test_logout_and_session_profile(client):
    client.post("/api/auth/login", json={
        "email": "citizen@example.com",
        "password": "Password@123"
    })
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["authenticated"] is True

    # Logout
    client.post("/api/auth/logout")
    me_after = client.get("/api/auth/me")
    assert me_after.get_json()["authenticated"] is False
