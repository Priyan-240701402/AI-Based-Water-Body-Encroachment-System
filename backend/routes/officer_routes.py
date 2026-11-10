"""
Officer Portal API Blueprint.
Endpoints for officer triage, verification, inspection records, and GIS route map.
"""

from flask import Blueprint, jsonify, session, request
from datetime import datetime, timezone
from backend.database import db
from backend.models.complaint import Complaint
from backend.models.history import ComplaintStatusHistory
from backend.models.authority import Authority
from backend.models.user import User
from backend.services.complaint_service import ComplaintService
from backend.utils.auth_helpers import officer_required, get_current_user

officer_bp = Blueprint("officer_api", __name__, url_prefix="/api/officer")

@officer_bp.route("/dashboard", methods=["GET"])
@officer_required
def officer_dashboard_stats():
    complaints = Complaint.query.all()
    stats = {
        "total_assigned": len(complaints),
        "pending_verification": sum(1 for c in complaints if c.status in ("ASSIGNED", "UNDER_VERIFICATION")),
        "high_priority": sum(1 for c in complaints if c.priority in ("HIGH", "CRITICAL")),
        "action_required": sum(1 for c in complaints if c.status == "ACTION_REQUIRED"),
        "resolved": sum(1 for c in complaints if c.status == "RESOLVED")
    }
    return jsonify({"success": True, "stats": stats}), 200

@officer_bp.route("/complaints", methods=["GET"])
@officer_required
def list_assigned_complaints():
    query = Complaint.query
    
    # Filter params
    status = request.args.get("status")
    priority = request.args.get("priority")
    water_body_id = request.args.get("water_body_id")
    search = request.args.get("search")

    if status:
        query = query.filter_by(status=status.upper())
    if priority:
        query = query.filter_by(priority=priority.upper())
    if water_body_id:
        query = query.filter_by(water_body_id=int(water_body_id))

    complaints = query.order_by(Complaint.created_at.desc()).all()

    if search:
        search_lower = search.lower()
        complaints = [c for c in complaints if search_lower in str(c.id) or search_lower in (c.title or "").lower()]

    return jsonify({
        "success": True,
        "count": len(complaints),
        "complaints": [c.to_dict() for c in complaints]
    }), 200

@officer_bp.route("/complaints/<int:complaint_id>", methods=["GET"])
@officer_required
def get_assigned_complaint(complaint_id: int):
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404

    data = complaint.to_dict()
    data["evidence"] = [e.to_dict() for e in complaint.evidence]
    data["status_history"] = [h.to_dict() for h in complaint.status_history]
    data["assignments"] = [a.to_dict() for a in complaint.assignments]
    return jsonify({"success": True, "complaint": data}), 200

@officer_bp.route("/complaints/<int:complaint_id>/verify", methods=["POST"])
@officer_required
def verify_complaint(complaint_id: int):
    user = get_current_user()
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404

    data = request.get_json() or {}
    outcome = data.get("outcome", "UNDER_VERIFICATION").strip()
    findings = data.get("findings", "").strip()
    remarks = data.get("remarks", "").strip()
    new_status = data.get("status")

    if not new_status:
        if outcome == "Verified — Further Action Required":
            new_status = "ACTION_REQUIRED"
        elif outcome == "No Encroachment Indicator Confirmed":
            new_status = "REJECTED"
        elif outcome == "Referred to Another Authority":
            new_status = "ASSIGNED"
        else:
            new_status = "UNDER_VERIFICATION"

    full_remarks = f"Verification Outcome: [{outcome}]. Findings: {findings}. Remarks: {remarks}"
    
    try:
        updated_complaint = ComplaintService.update_status(complaint_id, new_status, full_remarks, user.id)
        return jsonify({
            "success": True,
            "message": "Official verification recorded successfully.",
            "complaint": updated_complaint.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@officer_bp.route("/map", methods=["GET"])
@officer_required
def officer_map_data():
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    return jsonify({
        "success": True,
        "count": len(complaints),
        "complaints": [c.to_dict() for c in complaints]
    }), 200

@officer_bp.route("/inspections", methods=["GET"])
@officer_required
def officer_inspections_list():
    history = ComplaintStatusHistory.query.order_by(ComplaintStatusHistory.changed_at.desc()).all()
    return jsonify({
        "success": True,
        "count": len(history),
        "inspections": [h.to_dict() for h in history]
    }), 200
