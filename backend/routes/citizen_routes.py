"""
Citizen Portal API Blueprint.
Provides dedicated endpoints for Citizen complaints and tracking.
Strictly enforced for citizen ownership.
"""

from flask import Blueprint, jsonify, session, request
from backend.database import db
from backend.models.complaint import Complaint
from backend.utils.auth_helpers import citizen_required, get_current_user

citizen_bp = Blueprint("citizen_api", __name__, url_prefix="/api/citizen")

@citizen_bp.route("/complaints", methods=["GET"])
@citizen_required
def list_citizen_complaints():
    user = get_current_user()
    complaints = Complaint.query.filter_by(user_id=user.id).order_by(Complaint.created_at.desc()).all()
    return jsonify({
        "success": True,
        "count": len(complaints),
        "complaints": [c.to_dict() for c in complaints]
    }), 200

@citizen_bp.route("/complaints/<int:complaint_id>", methods=["GET"])
@citizen_required
def get_citizen_complaint(complaint_id: int):
    user = get_current_user()
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404
    
    # Ownership Check: Citizens can only view their own complaints
    if complaint.user_id != user.id and user.role != "admin":
        return jsonify({"success": False, "message": "Forbidden. You are not authorized to view this complaint."}), 403

    data = complaint.to_dict()
    data["evidence"] = [e.to_dict() for e in complaint.evidence]
    data["status_history"] = [h.to_dict() for h in complaint.status_history]
    return jsonify({"success": True, "complaint": data}), 200
