"""
AI Inference and Analysis API Blueprint.
Provides explicit triggers for:
- Forward Chaining Preliminary Analysis
- Backward Chaining Hypothesis Verification
- CSP Authority Assignment
- A* Search Route Calculation
"""

from flask import Blueprint, request, jsonify
from backend.database import db
from backend.models.complaint import Complaint
from backend.models.authority import Authority
from backend.models.assignment import AuthorityAssignment
from backend.services.complaint_service import ComplaintService
from backend.ai.astar import AStarSearch

ai_bp = Blueprint("ai_api", __name__, url_prefix="/api/complaints")

@ai_bp.route("/<int:complaint_id>/analyze", methods=["POST"])
def analyze_complaint(complaint_id: int):
    """
    Runs or re-runs Forward Chaining inference on the complaint facts.
    Returns the reasoning trace and updates the complaint classification and priority.
    """
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404

    result = ComplaintService.run_ai_analysis(complaint, complaint.water_body)
    
    # Update complaint
    complaint.classification = result["preliminary_result"]
    complaint.priority = result["priority"]
    if complaint.ai_reasoning_trace is None:
        complaint.ai_reasoning_trace = {}
    
    trace_copy = dict(complaint.ai_reasoning_trace)
    trace_copy["forward_chaining"] = result
    complaint.ai_reasoning_trace = trace_copy
    
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Forward Chaining preliminary reasoning executed.",
        "result": result
    }), 200

@ai_bp.route("/<int:complaint_id>/verify-backward", methods=["POST"])
def verify_backward(complaint_id: int):
    """
    Executes Backward Chaining to prove a hypothesis goal
    (default: 'REQUIRES_OFFICIAL_VERIFICATION').
    """
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404

    data = request.get_json() or {}
    goal = data.get("goal", "REQUIRES_OFFICIAL_VERIFICATION")

    proof_result = ComplaintService.verify_with_backward_chaining(complaint, goal)

    return jsonify({
        "success": True,
        "message": f"Backward Chaining verification executed for goal: '{goal}'.",
        "proof": proof_result
    }), 200

@ai_bp.route("/<int:complaint_id>/assign", methods=["POST"])
def assign_authority(complaint_id: int):
    """
    Re-runs CSP solver to assign or reassign an eligible authority.
    """
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404

    csp_result = ComplaintService.assign_authority_csp(complaint, complaint.water_body)
    
    if not csp_result.get("success"):
        return jsonify({
            "success": False,
            "message": csp_result.get("assignment_reason", "No eligible authority found."),
            "evaluation_log": csp_result.get("evaluation_log")
        }), 400

    auth_data = csp_result["assigned_authority"]
    
    # Record or update assignment
    existing_assignment = AuthorityAssignment.query.filter_by(complaint_id=complaint.id).first()
    if existing_assignment:
        existing_assignment.authority_id = auth_data["id"]
        existing_assignment.assignment_reason = csp_result["assignment_reason"]
        existing_assignment.assigned_by = "AI_CSP_SYSTEM"
    else:
        new_assign = AuthorityAssignment(
            complaint_id=complaint.id,
            authority_id=auth_data["id"],
            assigned_by="AI_CSP_SYSTEM",
            assignment_reason=csp_result["assignment_reason"]
        )
        db.session.add(new_assign)

    complaint.status = "ASSIGNED"
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "CSP Authority assignment resolved.",
        "assigned_authority": auth_data,
        "assignment_reason": csp_result["assignment_reason"],
        "evaluation_log": csp_result["evaluation_log"]
    }), 200

@ai_bp.route("/<int:complaint_id>/inspection-route", methods=["GET"])
def get_inspection_route(complaint_id: int):
    """
    A* Search route calculation from the assigned Authority Office to the Complaint location.
    """
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404

    # Default authority office coordinates (e.g. Metro Municipal HQ: 12.9716, 77.5946)
    office_lat = 12.9716
    office_lng = 77.5946
    
    # If assigned authority has known headquarters or zone center
    if complaint.assignments and complaint.assignments[0].authority:
        auth = complaint.assignments[0].authority
        if "North" in auth.jurisdiction:
            office_lat, office_lng = 13.0200, 77.5800
        elif "East" in auth.jurisdiction:
            office_lat, office_lng = 12.9600, 77.7100

    goal_lat = float(complaint.latitude)
    goal_lng = float(complaint.longitude)

    planner = AStarSearch()
    route = planner.find_route((office_lat, office_lng), (goal_lat, goal_lng))

    return jsonify({
        "success": True,
        "complaint_id": complaint_id,
        "route_plan": route
    }), 200
