"""
Security, Injection Resistance & Input Sanitation Tests.
Validates resistance to SQL Injection, Path Traversal, and sensitive credential protection.
"""

import pytest
import io
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

def test_sql_injection_attempt_in_login(client):
    """Verifies parameterized query resistance to SQL Injection in auth."""
    # Classical SQL injection payload
    sqli_payload = "' OR '1'='1' --"
    res = client.post("/api/auth/login", json={
        "email": sqli_payload,
        "password": "random_password"
    })
    # Must fail securely with 401, not 200 or 500
    assert res.status_code == 401

def test_sql_injection_attempt_in_complaint_search(client):
    """Verifies that search and filtering parameters are safely parameterized."""
    res = client.get("/api/complaints?status=' UNION SELECT * FROM users --")
    assert res.status_code == 200
    # Returns 0 results because status does not match literal string
    assert res.get_json()["count"] == 0

def test_no_credential_leak_in_user_api(client):
    """Verifies password hashes are never exposed in user dictionaries."""
    client.post("/api/auth/register", json={
        "name": "Secret User",
        "email": "secret@example.com",
        "password": "TopSecretPassword123",
        "role": "citizen"
    })
    res = client.post("/api/auth/login", json={
        "email": "secret@example.com",
        "password": "TopSecretPassword123"
    })
    user_dict = res.get_json()["user"]
    assert "password" not in user_dict
    assert "password_hash" not in user_dict

def test_file_upload_security_disallowed_extension(client):
    """Verifies rejection of dangerous file types (e.g. .exe, .sh, .py, .php)."""
    malicious_file = {
        "title": "Malicious Script Upload",
        "description": "Attempting exploit",
        "latitude": "12.9370",
        "longitude": "77.6720",
        "evidence": (io.BytesIO(b"malicious script payload"), "script.exe")
    }
    res = client.post("/api/complaints", data=malicious_file, content_type="multipart/form-data")
    # Must fail with 500 or 400 error and not save
    assert res.status_code in (400, 500)
    assert "File type not permitted" in res.get_json()["message"]

def test_file_upload_path_traversal_protection(client):
    """Verifies that path traversal filenames like '../../evil.jpg' are sanitized."""
    traversal_file = {
        "title": "Traversal Test",
        "description": "Checking filename sanitization",
        "latitude": "12.9370",
        "longitude": "77.6720",
        "evidence": (io.BytesIO(b"safe image content"), "../../etc/evil.jpg")
    }
    res = client.post("/api/complaints", data=traversal_file, content_type="multipart/form-data")
    assert res.status_code == 201
    c = res.get_json()["complaint"]
    evidence_res = client.get(f"/api/complaints/{c['id']}")
    ev_path = evidence_res.get_json()["complaint"]["evidence"][0]["file_path"]
    
    # Must NOT contain '..' or directory traversal markers
    assert ".." not in ev_path
    assert ev_path.startswith("uploads/")
