"""
Unit tests for Constraint Satisfaction Problem (CSP) Authority Assignment.
"""

import pytest
from backend.ai.csp import AuthorityCSP

def test_csp_valid_assignment():
    authorities = [
        {"id": 1, "name": "North Municipal", "department": "MUNICIPAL", "jurisdiction": "North Zone", "status": "ACTIVE", "max_active_cases": 15},
        {"id": 2, "name": "East Municipal", "department": "MUNICIPAL", "jurisdiction": "East Zone", "status": "ACTIVE", "max_active_cases": 20},
        {"id": 3, "name": "Central Revenue", "department": "REVENUE", "jurisdiction": "Central Zone", "status": "ACTIVE", "max_active_cases": 10},
    ]

    complaint = {
        "water_body_type": "LAKE",
        "district": "East Zone"
    }

    csp = AuthorityCSP(authorities)
    result = csp.solve(complaint)

    assert result["success"] is True
    assert result["assigned_authority"]["id"] == 2
    assert result["assigned_authority"]["department"] == "MUNICIPAL"
    assert "East Zone" in result["assignment_reason"]

def test_csp_overloaded_workload():
    """Verify that overloaded authority is skipped in favor of available capacity."""
    authorities = [
        {"id": 1, "name": "East Municipal A", "department": "MUNICIPAL", "jurisdiction": "East Zone", "status": "ACTIVE", "max_active_cases": 5},
        {"id": 2, "name": "East Revenue B", "department": "REVENUE", "jurisdiction": "East Zone", "status": "ACTIVE", "max_active_cases": 10},
    ]

    # Authority 1 is overloaded with 5 cases
    current_workloads = {1: 5, 2: 2}

    complaint = {
        "water_body_type": "LAKE",
        "district": "East Zone"
    }

    csp = AuthorityCSP(authorities, current_workloads)
    result = csp.solve(complaint)

    assert result["success"] is True
    # Should assign to Authority 2 because Authority 1 is at maximum capacity
    assert result["assigned_authority"]["id"] == 2
