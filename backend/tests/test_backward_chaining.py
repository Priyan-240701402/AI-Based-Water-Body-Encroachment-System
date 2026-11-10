"""
Unit tests for Backward Chaining Reasoning Engine.
"""

import pytest
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.backward_chaining import BackwardChainingEngine

def test_backward_chaining_goal_verification():
    """Verify that a target goal is proven recursively from facts."""
    facts = {
        "has_construction": True,
        "inside_boundary": True,
        "has_permission": False,
        "water_body_type": "LAKE"
    }

    kb = KnowledgeBase(initial_facts=facts)
    engine = BackwardChainingEngine(kb)
    
    # Prove sub-goal
    result1 = engine.verify_goal("POSSIBLE_ENCROACHMENT")
    assert result1["proven"] is True
    assert len(result1["proof_tree"]) > 0

    # Prove compound goal
    result2 = engine.verify_goal("REQUIRES_OFFICIAL_VERIFICATION")
    assert result2["proven"] is True

def test_backward_chaining_unproven_goal():
    """Verify unproven goal failure behavior."""
    facts = {
        "has_construction": False,
        "inside_boundary": False,
        "has_permission": True
    }

    kb = KnowledgeBase(initial_facts=facts)
    engine = BackwardChainingEngine(kb)
    result = engine.verify_goal("POSSIBLE_ENCROACHMENT")
    assert result["proven"] is False
