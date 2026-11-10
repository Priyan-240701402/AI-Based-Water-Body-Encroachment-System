"""
Propositional Logic Representation and Evaluator.

Handles propositional symbols, compound expressions (AND, OR, NOT),
and evaluation of rule conditions against known facts in the Knowledge Base.
"""

from typing import Dict, Any, Union, List

class PropositionalRule:
    """
    Represents a propositional Horn/Definite clause or conditional rule:
    Premises (conditions) -> Conclusion
    """
    def __init__(self, rule_id: str, description: str, conditions: Dict[str, Any], conclusion: str, priority: int = 1):
        self.rule_id = rule_id
        self.description = description
        self.conditions = conditions  # e.g., {"has_construction": True, "inside_boundary": True}
        self.conclusion = conclusion  # e.g., "POSSIBLE_ENCROACHMENT"
        self.priority = priority

    def evaluate(self, facts: Dict[str, Any]) -> bool:
        """
        Evaluates whether all conditions of this rule are satisfied by the current facts.
        Conditions can be:
        - Boolean equality: "has_construction": True
        - Value matching: "water_body_type": "CANAL"
        - Derived propositions: "POSSIBLE_ENCROACHMENT": True
        - Negation check: "has_permission": False
        """
        for var_name, expected_value in self.conditions.items():
            # If variable not present in facts, premise fails
            if var_name not in facts:
                return False
            
            actual_value = facts[var_name]
            
            # Handle boolean comparisons flexibly
            if isinstance(expected_value, bool) and isinstance(actual_value, str):
                actual_bool = actual_value.lower() in ("true", "yes", "1")
                if actual_bool != expected_value:
                    return False
            elif actual_value != expected_value:
                return False

        return True

    def get_premises_explanation(self, facts: Dict[str, Any]) -> List[str]:
        """Returns human-readable explanation of why this rule's conditions matched."""
        explanations = []
        for var_name, expected_value in self.conditions.items():
            actual = facts.get(var_name, "UNSET")
            explanations.append(f"{var_name} == {expected_value} (Matched: {actual})")
        return explanations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "conditions": self.conditions,
            "conclusion": self.conclusion,
            "priority": self.priority
        }
