"""
Knowledge-Based AI Reasoning Engine Package.
Modules:
- KnowledgeBase: Declarative fact and rule storage
- PropositionalRule: Logic propositions and condition evaluations
- ForwardChainingEngine: Main reasoning algorithm for deducing encroachment & generating audit trace
- BackwardChainingEngine: Goal verification and hypothesis testing
- AuthorityCSP: Constraint Satisfaction Problem authority assignment solver
- AStarSearch: Path finding for inspection route
"""

from backend.ai.propositional_logic import PropositionalRule
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.forward_chaining import ForwardChainingEngine
from backend.ai.backward_chaining import BackwardChainingEngine
from backend.ai.csp import AuthorityCSP
from backend.ai.astar import AStarSearch

__all__ = [
    "PropositionalRule",
    "KnowledgeBase",
    "ForwardChainingEngine",
    "BackwardChainingEngine",
    "AuthorityCSP",
    "AStarSearch",
]
