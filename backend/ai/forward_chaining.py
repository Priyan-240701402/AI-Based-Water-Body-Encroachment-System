"""
Forward Chaining Inference Engine (Main AI Reasoning Algorithm).

Applies data-driven reasoning starting from known atomic facts,
iteratively evaluating propositional Horn clauses, deducing new facts,
and building a complete explainable audit trace.
"""

from typing import Dict, Any, List
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.propositional_logic import PropositionalRule

class ForwardChainingEngine:
    """
    Classical Forward Chaining Inference Engine.
    Repeatedly fires candidate rules whose premises are satisfied by the current fact set,
    until no new facts can be derived (fixed-point termination).
    """

    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def run_inference(self) -> Dict[str, Any]:
        """
        Executes forward chaining algorithm.
        Returns:
            - initial_facts: starting facts
            - derived_facts: facts inferred by rules
            - fired_rules: list of rules that fired
            - trace: chronological step-by-step reasoning logs
            - preliminary_result: standardized category
            - priority_recommendation: recommended triage priority ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
        """
        # Working memory of facts
        current_facts = dict(self.kb.facts)
        initial_facts = dict(self.kb.facts)
        
        # Sort rules by priority (ascending order: priority 1 executes first)
        active_rules = sorted(self.kb.rules, key=lambda r: r.priority)
        
        fired_rules: List[str] = []
        reasoning_trace: List[Dict[str, Any]] = []
        step_number = 1

        # Fixed point iteration loop
        facts_changed = True
        while facts_changed:
            facts_changed = False
            for rule in active_rules:
                # If rule hasn't fired yet and premises evaluate to True
                if rule.rule_id not in fired_rules and rule.evaluate(current_facts):
                    # Fire rule
                    conclusion_name = rule.conclusion
                    # If this is a boolean conclusion, store as True
                    current_facts[conclusion_name] = True
                    fired_rules.append(rule.rule_id)
                    facts_changed = True

                    # Record step in trace
                    trace_entry = {
                        "step": step_number,
                        "rule_id": rule.rule_id,
                        "description": rule.description,
                        "conditions_satisfied": rule.get_premises_explanation(current_facts),
                        "derived_fact": conclusion_name,
                        "facts_state": dict(current_facts)
                    }
                    reasoning_trace.append(trace_entry)
                    step_number += 1

        # Classify preliminary result based strictly on derived propositions
        preliminary_result, priority_level = self._classify_result(current_facts, initial_facts)

        return {
            "initial_facts": initial_facts,
            "all_facts": current_facts,
            "derived_facts": {k: v for k, v in current_facts.items() if k not in initial_facts},
            "fired_rules": fired_rules,
            "reasoning_trace": reasoning_trace,
            "preliminary_result": preliminary_result,
            "priority": priority_level,
            "disclaimer": "This is an automated Knowledge-Based preliminary analysis. Legal confirmation requires official field survey."
        }

    def _classify_result(self, facts: Dict[str, Any], initial_facts: Dict[str, Any]) -> tuple[str, str]:
        """
        Synthesizes final preliminary outcome adhering strictly to the master prompt:
        - Possible Encroachment
        - Requires Official Verification
        - Insufficient Information
        - No Preliminary Encroachment Indicator
        """
        has_construction = initial_facts.get("has_construction", False)
        inside_boundary = initial_facts.get("inside_boundary", False)
        evidence_present = initial_facts.get("evidence_present", False)
        
        # Priority defaults
        priority = "MEDIUM"
        if facts.get("PRIORITY_HIGH", False) or facts.get("FLOW_OBSTRUCTION_RISK", False):
            priority = "HIGH"

        if facts.get("PERMITTED_ACTIVITY", False):
            return "Permitted Activity / Authorized", "LOW"

        if facts.get("REQUIRES_OFFICIAL_VERIFICATION", False):
            return "Requires Official Verification", priority

        if facts.get("POSSIBLE_ENCROACHMENT", False):
            return "Possible Encroachment", priority

        if facts.get("NO_PRELIMINARY_INDICATOR", False) or not has_construction:
            return "No Preliminary Encroachment Indicator", "LOW"

        # If data is inconclusive (e.g. reported construction but outside mapped boundary with no proof)
        if not inside_boundary and not evidence_present:
            return "Insufficient Information", "LOW"

        if not inside_boundary:
            return "No Preliminary Encroachment Indicator", "LOW"

        return "Requires Official Verification", priority
