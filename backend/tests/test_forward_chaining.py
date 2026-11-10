"""
Unit tests for Forward Chaining Inference Engine.
"""

import pytest
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.forward_chaining import ForwardChainingEngine

def test_forward_chaining_possible_encroachment():
    """Verify that Construction + InsideBoundary derives PossibleEncroachment and OfficialVerification."""
    facts = {
        "has_construction": True,
        "inside_boundary": True,
        "has_permission": False,
        "affected_area_level": "HIGH",
        "water_body_type": "LAKE",
        "district": "East Zone",
        "evidence_present": True
    }
    
    kb = KnowledgeBase(initial_facts=facts)
    engine = ForwardChainingEngine(kb)
    result = engine.run_inference()

    # Verify conclusions
    assert result["all_facts"].get("POSSIBLE_ENCROACHMENT") is True
    assert result["all_facts"].get("REQUIRES_OFFICIAL_VERIFICATION") is True
    assert result["preliminary_result"] == "Requires Official Verification"
    assert result["priority"] == "HIGH"

    # Verify trace exists
    trace = result["reasoning_trace"]
    assert len(trace) >= 2
    rule_ids = [entry["rule_id"] for entry in trace]
    assert "R001" in rule_ids
    assert "R002" in rule_ids

def test_forward_chaining_no_preliminary_indicator():
    """Verify that absence of construction and outside boundary derives No Indicator."""
    facts = {
        "has_construction": False,
        "inside_boundary": False,
        "has_permission": False,
        "affected_area_level": "LOW",
        "water_body_type": "POND",
        "district": "North Zone",
        "evidence_present": False
    }
    
    kb = KnowledgeBase(initial_facts=facts)
    engine = ForwardChainingEngine(kb)
    result = engine.run_inference()

    assert result["preliminary_result"] == "No Preliminary Encroachment Indicator"
    assert result["priority"] == "LOW"
