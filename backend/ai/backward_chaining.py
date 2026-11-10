"""
Backward Chaining Inference Engine (Supporting AI Algorithm).

Goal-driven reasoning used to verify a hypothesis (e.g., 'REQUIRES_OFFICIAL_VERIFICATION')
by recursively proving sub-goals and base facts from rules.
"""

from typing import Dict, Any, List, Set, Optional
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.propositional_logic import PropositionalRule

class BackwardChainingEngine:
    """
    Classical Backward Chaining Engine.
    Given a goal proposition, proves whether it holds true based on facts or rule chains.
    Produces an explanatory proof tree.
    """

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def verify_goal(self, goal: str) -> Dict[str, Any]:
        """
        Attempts to prove the specified goal.
        Returns verification outcome, proof tree, and missing premises (if unproven).
        """
        visited_goals: Set[str] = set()
        proof_tree: List[Dict[str, Any]] = []

        is_proven = self._prove(goal, visited_goals, proof_tree)

        return {
            "goal": goal,
            "proven": is_proven,
            "proof_tree": proof_tree,
            "explanation": (
                f"Goal '{goal}' successfully verified through rule deductions."
                if is_proven
                else f"Goal '{goal}' could NOT be proven from the current known facts and rules."
            )
        }

    def _prove(self, goal: str, visited_goals: Set[str], proof_tree: List[Dict[str, Any]]) -> bool:
        """Recursive helper to prove an individual goal proposition."""
        # 1. Base case: Goal is directly present in base facts as True
        if goal in self.kb.facts and self.kb.facts[goal] is True:
            proof_tree.append({
                "subgoal": goal,
                "status": "PROVEN_AS_BASE_FACT",
                "detail": f"'{goal}' is directly established in the knowledge base."
            })
            return True

        # Prevent circular reasoning loops
        if goal in visited_goals:
            return False
        visited_goals.add(goal)

        # 2. Find all rules whose conclusion is the goal
        candidate_rules = [r for r in self.kb.rules if r.conclusion == goal]
        if not candidate_rules:
            proof_tree.append({
                "subgoal": goal,
                "status": "UNPROVEN_NO_RULES",
                "detail": f"No rule or known fact exists to prove '{goal}'."
            })
            return False

        for rule in candidate_rules:
            all_premises_proven = True
            premise_proofs = []

            for var_name, expected_val in rule.conditions.items():
                # If premise is a known atomic fact matching value
                if var_name in self.kb.facts:
                    actual = self.kb.facts[var_name]
                    if actual == expected_val:
                        premise_proofs.append(f"Fact '{var_name}' matches expected {expected_val}.")
                    else:
                        all_premises_proven = False
                        break
                # Else if expected is True, attempt to recursively prove as sub-goal
                elif expected_val is True:
                    sub_proven = self._prove(var_name, visited_goals.copy(), proof_tree)
                    if sub_proven:
                        premise_proofs.append(f"Sub-goal '{var_name}' proven recursively.")
                    else:
                        all_premises_proven = False
                        break
                else:
                    all_premises_proven = False
                    break

            if all_premises_proven:
                proof_tree.append({
                    "subgoal": goal,
                    "status": "PROVEN_VIA_RULE",
                    "rule_id": rule.rule_id,
                    "rule_description": rule.description,
                    "premise_details": premise_proofs
                })
                return True

        proof_tree.append({
            "subgoal": goal,
            "status": "FAILED_PREMISES",
            "detail": f"Could not satisfy all premises for candidate rules deriving '{goal}'."
        })
        return False
