"""
Constraint Satisfaction Problem (CSP) Authority Assignment Suite.
Validates constraint satisfaction over Jurisdiction, Department, Status, and Workload.
"""

import pytest
from backend.ai.csp import AuthorityCSP

def test_csp_valid_single_candidate():
    authorities = [
        {"id": 1, "name": "East Municipal", "department": "MUNICIPAL", "jurisdiction": "East Zone", "status": "ACTIVE", "max_active_cases": 20},
        {"id": 2, "name": "North Municipal", "department": "MUNICIPAL", "jurisdiction": "North Zone", "status": "ACTIVE", "max_active_cases": 20},
    ]
    complaint = {
        "water_body_type": "LAKE",
        "district": "East Zone"
    }
    csp = AuthorityCSP(authorities)
    res = csp.solve(complaint)

    assert res["success"] is True
    assert res["assigned_authority"]["id"] == 1
    assert "East Zone" in res["assignment_reason"]

def test_csp_workload_capacity_selection():
    """When multiple authorities are eligible, chooses the one with higher capacity slack."""
    authorities = [
        {"id": 1, "name": "Auth Busy", "department": "MUNICIPAL", "jurisdiction": "Central Zone", "status": "ACTIVE", "max_active_cases": 10},
        {"id": 2, "name": "Auth Free", "department": "MUNICIPAL", "jurisdiction": "Central Zone", "status": "ACTIVE", "max_active_cases": 20},
    ]
    # Auth 1 has 9 cases (1 slack); Auth 2 has 2 cases (18 slack)
    current_workloads = {1: 9, 2: 2}
    complaint = {"water_body_type": "LAKE", "district": "Central Zone"}

    csp = AuthorityCSP(authorities, current_workloads)
    res = csp.solve(complaint)

    assert res["success"] is True
    assert res["assigned_authority"]["id"] == 2 # Selected the authority with 18 slack

def test_csp_no_eligible_authority_handling():
    """Returns failure gracefully when no authority matches jurisdiction or department."""
    authorities = [
        {"id": 1, "name": "South Auth", "department": "MUNICIPAL", "jurisdiction": "South Zone", "status": "ACTIVE", "max_active_cases": 10}
    ]
    # Complaint in West Zone
    complaint = {"water_body_type": "LAKE", "district": "West Zone"}

    csp = AuthorityCSP(authorities)
    res = csp.solve(complaint)

    assert res["success"] is False
    assert res["assigned_authority"] is None
    assert "No active authority satisfied" in res["assignment_reason"]
    assert len(res["evaluation_log"]) > 0

def test_csp_inactive_authority_rejected():
    authorities = [
        {"id": 1, "name": "Inactive Officer", "department": "MUNICIPAL", "jurisdiction": "North Zone", "status": "INACTIVE", "max_active_cases": 15}
    ]
    complaint = {"water_body_type": "LAKE", "district": "North Zone"}

    csp = AuthorityCSP(authorities)
    res = csp.solve(complaint)

    assert res["success"] is False
    assert any("Inactive status" in log for log in res["evaluation_log"])

def test_csp_department_type_constraint():
    """Canals require Water Resources or Municipal; Environmental only is not eligible."""
    authorities = [
        {"id": 1, "name": "Pollution Board Only", "department": "ENVIRONMENTAL", "jurisdiction": "Central Zone", "status": "ACTIVE", "max_active_cases": 20}
    ]
    complaint = {"water_body_type": "CANAL", "district": "Central Zone"}

    csp = AuthorityCSP(authorities)
    res = csp.solve(complaint)

    assert res["success"] is False
    assert any("not eligible" in log for log in res["evaluation_log"])
