"""
Knowledge Base for Water Body Encroachment Reasoning Engine.
Maintains facts and propositional rules extracted from complaint data.
"""

from typing import Dict, Any, List
from backend.ai.propositional_logic import PropositionalRule

class KnowledgeBase:
    """
    Modular Knowledge Base containing:
    1. Facts: Current known attributes of a specific complaint/water body.
    2. Rules: Propositional implication rules (Conditions -> Conclusion).
    """

    DEFAULT_RULES = [
        PropositionalRule(
            rule_id="R001",
            description="Construction reported inside or intersecting water body boundary indicates potential encroachment",
            conditions={"has_construction": True, "inside_boundary": True},
            conclusion="POSSIBLE_ENCROACHMENT",
            priority=1
        ),
        PropositionalRule(
            rule_id="R002",
            description="Possible encroachment lacking official authorization requires physical field verification",
            conditions={"POSSIBLE_ENCROACHMENT": True, "has_permission": False},
            conclusion="REQUIRES_OFFICIAL_VERIFICATION",
            priority=2
        ),
        PropositionalRule(
            rule_id="R003",
            description="High severity impact or critical zone marks complaint as HIGH priority",
            conditions={"REQUIRES_OFFICIAL_VERIFICATION": True, "affected_area_level": "HIGH"},
            conclusion="PRIORITY_HIGH",
            priority=3
        ),
        PropositionalRule(
            rule_id="R004",
            description="Construction obstructing canal drainage path triggers flood hazard indicator",
            conditions={"water_body_type": "CANAL", "has_construction": True},
            conclusion="FLOW_OBSTRUCTION_RISK",
            priority=2
        ),
        PropositionalRule(
            rule_id="R005",
            description="Activities with valid authorized permit are marked as legal/permitted",
            conditions={"has_construction": True, "has_permission": True},
            conclusion="PERMITTED_ACTIVITY",
            priority=2
        ),
        PropositionalRule(
            rule_id="R006",
            description="Reports with no physical construction and outside boundary have no preliminary indicators",
            conditions={"has_construction": False, "inside_boundary": False},
            conclusion="NO_PRELIMINARY_INDICATOR",
            priority=1
        )
    ]

    def __init__(self, initial_facts: Dict[str, Any] = None, rules: List[PropositionalRule] = None):
        self.facts: Dict[str, Any] = initial_facts.copy() if initial_facts else {}
        self.rules: List[PropositionalRule] = rules if rules is not None else self.DEFAULT_RULES.copy()

    def add_fact(self, name: str, value: Any):
        """Adds or updates a fact in the knowledge base."""
        self.facts[name] = value

    def get_fact(self, name: str, default: Any = None) -> Any:
        return self.facts.get(name, default)

    def add_rule(self, rule: PropositionalRule):
        self.rules.append(rule)

    @classmethod
    def from_complaint(cls, complaint_data: Dict[str, Any], custom_rules: List[PropositionalRule] = None) -> "KnowledgeBase":
        """
        Factory helper to extract standardized symbolic facts from a complaint dictionary/object.
        """
        facts = {
            "has_construction": bool(complaint_data.get("has_construction", False)),
            "inside_boundary": bool(complaint_data.get("inside_boundary", False)),
            "has_permission": bool(complaint_data.get("has_permission", False)),
            "affected_area_level": str(complaint_data.get("affected_area_level", "MEDIUM")).upper(),
            "water_body_type": str(complaint_data.get("water_body_type", "LAKE")).upper(),
            "district": str(complaint_data.get("district", "Central Zone")),
            "evidence_present": bool(complaint_data.get("evidence_count", 0) > 0 or complaint_data.get("has_evidence", False)),
        }
        return cls(initial_facts=facts, rules=custom_rules)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "facts": self.facts,
            "rules": [r.to_dict() for r in self.rules]
        }
