"""
Forward Chaining & Propositional Logic AI Validation Suite.
Implements the formal AI test matrix (AI-001 through AI-008).
"""

import pytest
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.forward_chaining import ForwardChainingEngine
from backend.ai.propositional_logic import PropositionalRule

def test_ai_001_construction_inside_boundary_no_permission():
    """AI-001: Construction=YES, InsideBoundary=YES, Permission=NO -> Possible Encroachment & Verification Required."""
    facts = {
        "has_construction": True,
        "inside_boundary": True,
        "has_permission": False,
        "affected_area_level": "MEDIUM",
        "water_body_type": "LAKE",
        "evidence_present": True
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = ForwardChainingEngine(kb)
    result = engine.run_inference()

    assert result["all_facts"].get("POSSIBLE_ENCROACHMENT") is True
    assert result["all_facts"].get("REQUIRES_OFFICIAL_VERIFICATION") is True
    assert result["preliminary_result"] == "Requires Official Verification"
    assert len(result["reasoning_trace"]) >= 2
    # Verify non-confirmatory phrasing
    assert "Legal confirmation requires official field survey" in result["disclaimer"]

def test_ai_002_no_construction_inside_boundary():
    """AI-002: Construction=NO, InsideBoundary=YES -> No Preliminary Indicator."""
    facts = {
        "has_construction": False,
        "inside_boundary": True,
        "has_permission": False,
        "affected_area_level": "LOW",
        "water_body_type": "LAKE",
        "evidence_present": False
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = ForwardChainingEngine(kb)
    result = engine.run_inference()

    assert result["all_facts"].get("POSSIBLE_ENCROACHMENT") is None
    assert result["preliminary_result"] == "No Preliminary Encroachment Indicator"

def test_ai_003_construction_outside_boundary():
    """AI-003: Construction=YES, InsideBoundary=NO, no evidence -> Insufficient Information / No Indicator."""
    facts = {
        "has_construction": True,
        "inside_boundary": False,
        "has_permission": False,
        "affected_area_level": "LOW",
        "water_body_type": "LAKE",
        "evidence_present": False
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = ForwardChainingEngine(kb)
    result = engine.run_inference()

    assert result["all_facts"].get("POSSIBLE_ENCROACHMENT") is None
    assert result["preliminary_result"] == "Insufficient Information"

def test_ai_004_construction_with_authorized_permission():
    """AI-004: Construction=YES, InsideBoundary=YES, Permission=YES -> Permitted Activity."""
    facts = {
        "has_construction": True,
        "inside_boundary": True,
        "has_permission": True,
        "affected_area_level": "MEDIUM",
        "water_body_type": "LAKE",
        "evidence_present": True
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = ForwardChainingEngine(kb)
    result = engine.run_inference()

    assert result["all_facts"].get("PERMITTED_ACTIVITY") is True
    assert result["preliminary_result"] == "Permitted Activity / Authorized"
    assert result["priority"] == "LOW"

def test_ai_005_no_construction_outside_boundary():
    """AI-005: Construction=NO, InsideBoundary=NO -> No Preliminary Encroachment Indicator."""
    facts = {
        "has_construction": False,
        "inside_boundary": False,
        "has_permission": False,
        "affected_area_level": "LOW",
        "water_body_type": "LAKE",
        "evidence_present": False
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = ForwardChainingEngine(kb)
    result = engine.run_inference()

    assert result["all_facts"].get("NO_PRELIMINARY_INDICATOR") is True
    assert result["preliminary_result"] == "No Preliminary Encroachment Indicator"

def test_ai_006_canal_flow_obstruction_rule():
    """AI-006: Canal with construction -> FLOW_OBSTRUCTION_RISK derived and High Priority."""
    facts = {
        "has_construction": True,
        "inside_boundary": True,
        "has_permission": False,
        "water_body_type": "CANAL",
        "affected_area_level": "MEDIUM",
        "evidence_present": True
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = ForwardChainingEngine(kb)
    result = engine.run_inference()

    assert result["all_facts"].get("FLOW_OBSTRUCTION_RISK") is True
    assert result["priority"] == "HIGH"

def test_ai_007_high_severity_escalation():
    """AI-007: Affected Area HIGH -> PRIORITY_HIGH rule fires."""
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
    result = engine.run_inference()

    assert result["all_facts"].get("PRIORITY_HIGH") is True
    assert result["priority"] == "HIGH"

def test_ai_008_reasoning_trace_and_determinism():
    """AI-008: Verify determinism and trace structure."""
    facts = {
        "has_construction": True,
        "inside_boundary": True,
        "has_permission": False,
        "affected_area_level": "HIGH",
        "water_body_type": "LAKE",
        "evidence_present": True
    }
    kb1 = KnowledgeBase(initial_facts=facts)
    res1 = ForwardChainingEngine(kb1).run_inference()

    kb2 = KnowledgeBase(initial_facts=facts)
    res2 = ForwardChainingEngine(kb2).run_inference()

    # Determinism: Must produce identical conclusions and trace steps
    assert res1["preliminary_result"] == res2["preliminary_result"]
    assert res1["fired_rules"] == res2["fired_rules"]
    assert len(res1["reasoning_trace"]) == len(res2["reasoning_trace"])
    
    # Trace verification
    for step in res1["reasoning_trace"]:
        assert "step" in step
        assert "rule_id" in step
        assert "derived_fact" in step
        assert len(step["conditions_satisfied"]) > 0
