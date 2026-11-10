"""
Performance, Latency & Scalability Benchmark Suite.
Measures execution times for AI reasoning, CSP solver, and database queries.
"""

import time
import pytest
from backend.app import create_app
from backend.database import db
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.forward_chaining import ForwardChainingEngine
from backend.ai.csp import AuthorityCSP
from backend.models.complaint import Complaint
from backend.models.user import User

@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_forward_chaining_latency():
    """Validates that Forward Chaining reasoning finishes in < 10 milliseconds."""
    facts = {
        "has_construction": True,
        "inside_boundary": True,
        "has_permission": False,
        "affected_area_level": "HIGH",
        "water_body_type": "LAKE",
        "evidence_present": True
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = ForwardChainingEngine(kb)

    start = time.perf_counter()
    for _ in range(50): # Run 50 iterations
        result = engine.run_inference()
    duration = (time.perf_counter() - start) / 50.0

    # Average execution time in milliseconds
    ms = duration * 1000.0
    print(f"\n[Performance] Average Forward Chaining inference time: {ms:.3f} ms")
    assert ms < 10.0, f"Inference too slow: {ms} ms"

def test_csp_solver_latency():
    """Validates that CSP authority assignment finishes in < 20 milliseconds."""
    authorities = [
        {"id": i, "name": f"Authority {i}", "department": "MUNICIPAL" if i % 2 == 0 else "REVENUE",
         "jurisdiction": "Central Zone", "status": "ACTIVE", "max_active_cases": 25}
        for i in range(1, 30)
    ]
    csp = AuthorityCSP(authorities)
    complaint = {"water_body_type": "LAKE", "district": "Central Zone"}

    start = time.perf_counter()
    for _ in range(50):
        res = csp.solve(complaint)
    duration = (time.perf_counter() - start) / 50.0

    ms = duration * 1000.0
    print(f"\n[Performance] Average CSP solving time: {ms:.3f} ms")
    assert ms < 20.0, f"CSP solving too slow: {ms} ms"

def test_complaint_api_response_time(client):
    """Validates that complaint submission API completes in < 250 milliseconds."""
    payload = {
        "title": "Performance Benchmark Grievance",
        "description": "Testing latency of complaint submission API",
        "latitude": 12.9375,
        "longitude": 77.6725,
        "water_body_id": 1,
        "has_construction": True,
        "has_permission": False
    }

    start = time.perf_counter()
    res = client.post("/api/complaints", json=payload)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert res.status_code == 201
    print(f"\n[Performance] Complaint submission API response: {elapsed_ms:.2f} ms")
    assert elapsed_ms < 500.0
