"""
Complaint Service.
Orchestrates complaint creation, AI reasoning engine execution,
authority assignment via CSP, and status lifecycle auditing.
"""

from typing import Dict, Any, Optional, List
from backend.database import db
from backend.models.complaint import Complaint
from backend.models.water_body import WaterBody
from backend.models.authority import Authority
from backend.models.assignment import AuthorityAssignment
from backend.models.history import ComplaintStatusHistory
from backend.models.evidence import ComplaintEvidence
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.forward_chaining import ForwardChainingEngine
from backend.ai.backward_chaining import BackwardChainingEngine
from backend.ai.csp import AuthorityCSP
from backend.services.map_service import MapService

class ComplaintService:

    @classmethod
    def create_complaint(cls, user_id: int, data: Dict[str, Any], files: List[Any] = None) -> Complaint:
        """
        Creates a complaint, processes location boundary, triggers Forward Chaining
        reasoning, applies CSP authority assignment, and logs audit history.
        """
        lat = float(data.get("latitude"))
        lng = float(data.get("longitude"))
        water_body_id = data.get("water_body_id")
        
        water_body = db.session.get(WaterBody, water_body_id) if water_body_id else None
        
        # 1. Spatial Boundary Check
        inside_boundary, boundary_note = MapService.check_boundary_intersection(lat, lng, water_body)

        has_construction = bool(data.get("has_construction", True))
        has_permission = bool(data.get("has_permission", False))
        affected_area_level = str(data.get("affected_area_level", "MEDIUM")).upper()

        complaint = Complaint(
            user_id=user_id,
            water_body_id=water_body.id if water_body else None,
            title=data.get("title", "Suspected Water Body Encroachment"),
            description=data.get("description", ""),
            latitude=lat,
            longitude=lng,
            has_construction=has_construction,
            inside_boundary=inside_boundary,
            has_permission=has_permission,
            affected_area_level=affected_area_level,
            status="SUBMITTED"
        )
        db.session.add(complaint)
        db.session.flush() # Flush to receive complaint.id

        # 2. Attach Evidence files if provided
        if files:
            from backend.utils.file_storage import save_evidence_file
            for f in files:
                if f and f.filename:
                    rel_path, mime, orig_name = save_evidence_file(f)
                    ev = ComplaintEvidence(
                        complaint_id=complaint.id,
                        file_path=rel_path,
                        file_type=mime,
                        original_filename=orig_name
                    )
                    db.session.add(ev)
            db.session.flush()

        # 3. Run AI Knowledge-Based Forward Chaining Engine
        ai_result = cls.run_ai_analysis(complaint, water_body)
        complaint.classification = ai_result["preliminary_result"]
        complaint.priority = ai_result["priority"]
        complaint.status = "AI_REVIEWED"

        # 4. Run CSP for Authority Assignment
        csp_result = cls.assign_authority_csp(complaint, water_body)
        
        # Combine reasoning and assignment into ai_reasoning_trace
        complaint.ai_reasoning_trace = {
            "forward_chaining": ai_result,
            "csp_assignment": csp_result,
            "boundary_check": {
                "inside_boundary": inside_boundary,
                "note": boundary_note
            }
        }

        # If CSP found eligible authority, update status to ASSIGNED
        if csp_result.get("success") and csp_result.get("assigned_authority"):
            auth_data = csp_result["assigned_authority"]
            assignment = AuthorityAssignment(
                complaint_id=complaint.id,
                authority_id=auth_data["id"],
                assigned_by="AI_CSP_SYSTEM",
                assignment_reason=csp_result.get("assignment_reason"),
                status="ASSIGNED"
            )
            db.session.add(assignment)
            complaint.status = "ASSIGNED"

        # 5. Record initial history entry
        history_entry = ComplaintStatusHistory(
            complaint_id=complaint.id,
            old_status=None,
            new_status=complaint.status,
            remarks=f"Complaint lodged. AI analysis: {complaint.classification}. Priority: {complaint.priority}.",
            changed_by=user_id
        )
        db.session.add(history_entry)

        db.session.commit()
        return complaint

    @classmethod
    def run_ai_analysis(cls, complaint: Complaint, water_body: Optional[WaterBody] = None) -> Dict[str, Any]:
        """Runs Forward Chaining inference on the complaint facts."""
        district = water_body.district if water_body else "Central Zone"
        wb_type = water_body.type if water_body else "LAKE"

        complaint_dict = {
            "has_construction": complaint.has_construction,
            "inside_boundary": complaint.inside_boundary,
            "has_permission": complaint.has_permission,
            "affected_area_level": complaint.affected_area_level,
            "water_body_type": wb_type,
            "district": district,
            "has_evidence": len(complaint.evidence) > 0 if complaint.evidence else False
        }

        kb = KnowledgeBase.from_complaint(complaint_dict)
        engine = ForwardChainingEngine(kb)
        return engine.run_inference()

    @classmethod
    def verify_with_backward_chaining(cls, complaint: Complaint, goal: str = "REQUIRES_OFFICIAL_VERIFICATION") -> Dict[str, Any]:
        """Uses Backward Chaining to verify a target goal proposition."""
        water_body = complaint.water_body
        district = water_body.district if water_body else "Central Zone"
        wb_type = water_body.type if water_body else "LAKE"

        complaint_dict = {
            "has_construction": complaint.has_construction,
            "inside_boundary": complaint.inside_boundary,
            "has_permission": complaint.has_permission,
            "affected_area_level": complaint.affected_area_level,
            "water_body_type": wb_type,
            "district": district,
            "has_evidence": len(complaint.evidence) > 0 if complaint.evidence else False
        }

        kb = KnowledgeBase.from_complaint(complaint_dict)
        engine = BackwardChainingEngine(kb)
        return engine.verify_goal(goal)

    @classmethod
    def assign_authority_csp(cls, complaint: Complaint, water_body: Optional[WaterBody] = None) -> Dict[str, Any]:
        """Uses CSP solver to select eligible authority for the complaint."""
        authorities = [a.to_dict() for a in Authority.query.all()]
        
        # Calculate active workloads
        active_assignments = (
            db.session.query(AuthorityAssignment.authority_id, db.func.count(AuthorityAssignment.id))
            .filter(AuthorityAssignment.status == "ASSIGNED")
            .group_by(AuthorityAssignment.authority_id)
            .all()
        )
        current_workloads = {auth_id: count for auth_id, count in active_assignments}

        complaint_info = {
            "water_body_type": water_body.type if water_body else "LAKE",
            "district": water_body.district if water_body else "Central Zone"
        }

        csp = AuthorityCSP(authorities, current_workloads)
        return csp.solve(complaint_info)

    @classmethod
    def update_status(cls, complaint_id: int, new_status: str, remarks: str, user_id: int) -> Complaint:
        """Updates complaint status and adds to audit history."""
        complaint = db.session.get(Complaint, complaint_id)
        if not complaint:
            from flask import abort
            abort(404)
        old_status = complaint.status
        complaint.status = new_status

        history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status=new_status,
            remarks=remarks,
            changed_by=user_id
        )
        db.session.add(history)
        db.session.commit()
        return complaint
