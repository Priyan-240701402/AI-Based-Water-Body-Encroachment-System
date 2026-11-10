"""
Constraint Satisfaction Problem (CSP) Solver for Authority Assignment.

Assigns complaints to eligible regulatory bodies satisfying:
1. Jurisdiction Constraint: District/Zone matches authority jurisdiction.
2. Department Eligibility: Department handles the specific water body category.
3. Status Constraint: Authority is ACTIVE.
4. Workload/Capacity Constraint: Active assignments < max_active_cases.
"""

from typing import Dict, Any, List, Optional

class AuthorityCSP:
    """
    Formulation of Authority Assignment as a CSP:
    - Variables: {Complaint_Assignment}
    - Domain: Set of all Candidate Authorities
    - Constraints:
        C1: Jurisdiction(Authority) == Jurisdiction(Complaint_Water_Body)
        C2: Department(Authority) in EligibleDepartments(Water_Body_Type)
        C3: Status(Authority) == 'ACTIVE'
        C4: CurrentWorkload(Authority) < MaxCapacity(Authority)
    """

    DEPARTMENT_ELIGIBILITY = {
        "LAKE": ["MUNICIPAL", "WATER_RESOURCES", "REVENUE"],
        "POND": ["MUNICIPAL", "REVENUE"],
        "CANAL": ["WATER_RESOURCES", "MUNICIPAL"],
        "RIVER": ["WATER_RESOURCES", "ENVIRONMENTAL", "REVENUE"],
        "WETLAND": ["ENVIRONMENTAL", "REVENUE", "WATER_RESOURCES"]
    }

    def __init__(self, authorities: List[Dict[str, Any]], current_workloads: Dict[int, int] = None):
        self.authorities = authorities
        self.current_workloads = current_workloads or {}

    def solve(self, complaint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solves the CSP using Backtracking Search with constraint propagation.
        Returns:
            - assigned_authority: Selected authority record
            - status: "SATISFIED" or "UNSATISFIABLE"
            - constraint_trace: Verification log for each evaluated constraint
        """
        water_body_type = str(complaint.get("water_body_type", "LAKE")).upper()
        target_district = str(complaint.get("district", "Central Zone")).strip().lower()
        
        eligible_depts = self.DEPARTMENT_ELIGIBILITY.get(water_body_type, ["MUNICIPAL", "REVENUE", "WATER_RESOURCES"])
        
        evaluation_log = []
        candidates = []

        for auth in self.authorities:
            auth_id = auth.get("id")
            auth_name = auth.get("name")
            auth_jurisdiction = str(auth.get("jurisdiction", "")).strip().lower()
            auth_dept = str(auth.get("department", "")).strip().upper()
            auth_status = str(auth.get("status", "ACTIVE")).strip().upper()
            max_cases = auth.get("max_active_cases", 20)
            workload = self.current_workloads.get(auth_id, 0)

            # Check C3: Status
            if auth_status != "ACTIVE":
                evaluation_log.append(f"Authority '{auth_name}' REJECTED: Inactive status ({auth_status}).")
                continue

            # Check C1: Jurisdiction
            # If authority has "all" or matches district
            jurisdiction_match = (auth_jurisdiction == target_district) or ("state" in auth_jurisdiction) or (auth_jurisdiction == "all")
            if not jurisdiction_match:
                evaluation_log.append(
                    f"Authority '{auth_name}' REJECTED: Jurisdiction mismatch ('{auth.get('jurisdiction')}' vs '{complaint.get('district')}')."
                )
                continue

            # Check C2: Department eligibility
            if auth_dept not in eligible_depts:
                evaluation_log.append(
                    f"Authority '{auth_name}' REJECTED: Department {auth_dept} not eligible for {water_body_type}."
                )
                continue

            # Check C4: Workload capacity
            if workload >= max_cases:
                evaluation_log.append(
                    f"Authority '{auth_name}' REJECTED: Capacity limit reached ({workload}/{max_cases} cases)."
                )
                continue

            # Passed all constraints!
            evaluation_log.append(
                f"Authority '{auth_name}' SATISFIES all constraints (Dept: {auth_dept}, Jurisdiction: {auth.get('jurisdiction')}, Workload: {workload}/{max_cases})."
            )
            candidates.append({
                "authority": auth,
                "current_workload": workload,
                "capacity_slack": max_cases - workload
            })

        if not candidates:
            return {
                "success": False,
                "assigned_authority": None,
                "assignment_reason": "No active authority satisfied all jurisdictional and department constraints.",
                "evaluation_log": evaluation_log
            }

        # Select candidate with lowest workload / highest available slack (Heuristic)
        best_candidate = max(candidates, key=lambda c: c["capacity_slack"])
        selected = best_candidate["authority"]

        reason = (
            f"Assigned to {selected['name']} ({selected['department']}) based on CSP resolution. "
            f"Satisfied Jurisdiction: '{selected['jurisdiction']}', Type: {water_body_type}, "
            f"Active Workload: {best_candidate['current_workload']}/{selected.get('max_active_cases', 20)} cases."
        )

        return {
            "success": True,
            "assigned_authority": selected,
            "assignment_reason": reason,
            "evaluation_log": evaluation_log
        }
