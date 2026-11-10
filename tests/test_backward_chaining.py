"""
Backward Chaining Goal Verification Suite.
Validates hypothesis testing, recursive premise proving, and proof tree generation.
"""

import pytest
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.backward_chaining import BackwardChainingEngine

def test_backward_chaining_proven_hypothesis():
    """Starts with Goal = REQUIRES_OFFICIAL_VERIFICATION and verifies chain of premises."""
    facts = {
        "has_construction": True,
        "inside_boundary": True,
        "has_permission": False,
        "water_body_type": "LAKE"
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = BackwardChainingEngine(kb)
    
    # 1. Test subgoal
    res_sub = engine.verify_goal("POSSIBLE_ENCROACHMENT")
    assert res_sub["proven"] is True
    assert res_sub["goal"] == "POSSIBLE_ENCROACHMENT"

    # 2. Test top-level goal
    res_top = engine.verify_goal("REQUIRES_OFFICIAL_VERIFICATION")
    assert res_top["proven"] is True
    assert len(res_top["proof_tree"]) > 0
    
    # Check that proof tree contains rule details
    proven_rules = [node.get("rule_id") for node in res_top["proof_tree"] if "rule_id" in node]
    assert "R001" in proven_rules or "R002" in proven_rules

def test_backward_chaining_unproven_hypothesis():
    """Tests goal failure when essential facts are missing or false."""
    facts = {
        "has_construction": False, # No construction
        "inside_boundary": True,
        "has_permission": False
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = BackwardChainingEngine(kb)

    res = engine.verify_goal("POSSIBLE_ENCROACHMENT")
    assert res["proven"] is False
    assert "could NOT be proven" in res["explanation"]

def test_backward_chaining_base_fact_lookup():
    """Tests goal that is directly established in the knowledge base."""
    facts = {
        "CUSTOM_FACT": True
    }
    kb = KnowledgeBase(initial_facts=facts)
    engine = BackwardChainingEngine(kb)
    res = engine.verify_goal("CUSTOM_FACT")
    assert res["proven"] is True
    assert res["proof_tree"][0]["status"] == "PROVEN_AS_BASE_FACT"
