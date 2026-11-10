"""
Complaint Management API Blueprint.
CRUD operations, status transitions, and audit logs.
"""

from flask import Blueprint, request, jsonify, session
from backend.database import db
from backend.models.complaint import Complaint
from backend.models.user import User
from backend.services.complaint_service import ComplaintService
from backend.utils.auth_helpers import login_required, role_required

complaint_bp = Blueprint("complaint_api", __name__, url_prefix="/api/complaints")

@complaint_bp.route("", methods=["POST"])
def create_complaint():
    """
    Submits a new complaint.
    Supports both JSON and Multipart Form Data (for uploading image/evidence).
    """
    user_id = session.get("user_id")
    if not user_id:
        # Check if citizen email provided or fallback to default citizen
        data = request.form if request.form else (request.get_json() or {})
        email = data.get("email")
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                user_id = user.id
        if not user_id:
            demo_user = User.query.filter_by(role="citizen").first() or User.query.first()
            if not demo_user:
                demo_user = User(name="System Citizen", email="citizen_system_fallback@example.com", password_hash="hash", role="citizen")
                db.session.add(demo_user)
                db.session.commit()
            user_id = demo_user.id

    # Extract form or JSON data
    if request.is_json:
        data = request.get_json() or {}
        files = []
    else:
        data = request.form.to_dict()
        files = request.files.getlist("evidence")

    # Validate mandatory coordinates and title
    try:
        lat = float(data.get("latitude", 0))
        lng = float(data.get("longitude", 0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid latitude and longitude coordinates."}), 400

    if lat == 0 and lng == 0:
        return jsonify({"success": False, "message": "Latitude and longitude coordinates are required."}), 400

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()

    if not title or not description:
        return jsonify({"success": False, "message": "Title and description are required."}), 400

    # Parse boolean flags
    def parse_bool(val):
        if isinstance(val, bool):
            return val
        return str(val).lower() in ("true", "1", "yes", "on")

    data_payload = {
        "title": title,
        "description": description,
        "latitude": lat,
        "longitude": lng,
        "water_body_id": int(data.get("water_body_id")) if data.get("water_body_id") else None,
        "has_construction": parse_bool(data.get("has_construction", True)),
        "has_permission": parse_bool(data.get("has_permission", False)),
        "affected_area_level": data.get("affected_area_level", "MEDIUM"),
    }

    try:
        complaint = ComplaintService.create_complaint(user_id, data_payload, files)
        return jsonify({
            "success": True,
            "message": "Complaint lodged and AI preliminary analysis executed.",
            "complaint": complaint.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error filing complaint: {str(e)}"}), 500

@complaint_bp.route("", methods=["GET"])
def list_complaints():
    """Returns list of complaints with optional query filters."""
    query = Complaint.query

    # Role-based restriction: citizens can only see their own complaints by default
    current_user_id = session.get("user_id")
    current_role = session.get("user_role")
    
    # If citizen is logged in and not admin/authority, filter to their complaints
    if current_role == "citizen" and current_user_id:
        query = query.filter_by(user_id=current_user_id)
    elif request.args.get("user_id"):
        query = query.filter_by(user_id=int(request.args.get("user_id")))

    # Filters
    if request.args.get("status"):
        query = query.filter_by(status=request.args.get("status"))
    if request.args.get("priority"):
        query = query.filter_by(priority=request.args.get("priority"))
    if request.args.get("water_body_id"):
        query = query.filter_by(water_body_id=int(request.args.get("water_body_id")))

    complaints = query.order_by(Complaint.created_at.desc()).all()
    return jsonify({
        "success": True,
        "count": len(complaints),
        "complaints": [c.to_dict() for c in complaints]
    }), 200

@complaint_bp.route("/<int:complaint_id>", methods=["GET"])
def get_complaint(complaint_id: int):
    """Retrieves full details of a complaint, including evidence and status history."""
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404

    data = complaint.to_dict()
    data["evidence"] = [e.to_dict() for e in complaint.evidence]
    data["status_history"] = [h.to_dict() for h in complaint.status_history]
    data["assignments"] = [a.to_dict() for a in complaint.assignments]

    return jsonify({"success": True, "complaint": data}), 200

@complaint_bp.route("/<int:complaint_id>", methods=["PUT"])
def update_complaint(complaint_id: int):
    """Updates fields of an existing complaint (title, description, priority, affected_area_level)."""
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404

    data = request.get_json() or {}
    if "title" in data:
        complaint.title = data["title"].strip() or complaint.title
    if "description" in data:
        complaint.description = data["description"].strip() or complaint.description
    if "priority" in data:
        valid_priorities = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        if data["priority"].upper() in valid_priorities:
            complaint.priority = data["priority"].upper()
    if "affected_area_level" in data:
        valid_levels = ("LOW", "MEDIUM", "HIGH")
        if data["affected_area_level"].upper() in valid_levels:
            complaint.affected_area_level = data["affected_area_level"].upper()

    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Complaint updated successfully.",
        "complaint": complaint.to_dict()
    }), 200

@complaint_bp.route("/<int:complaint_id>/status", methods=["PUT"])
def update_status(complaint_id: int):
    """Updates complaint status and logs remarks."""
    data = request.get_json() or {}
    new_status = data.get("status")
    remarks = data.get("remarks", "Status updated by authorized official.")
    
    if not new_status:
        return jsonify({"success": False, "message": "New status is required."}), 400

    user_id = session.get("user_id", 1) # Default to 1 if anonymous test
    try:
        complaint = ComplaintService.update_status(complaint_id, new_status, remarks, user_id)
        return jsonify({
            "success": True,
            "message": f"Status updated to {new_status}.",
            "complaint": complaint.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@complaint_bp.route("/<int:complaint_id>/history", methods=["GET"])
def get_complaint_history(complaint_id: int):
    """Retrieves history audit trail for a complaint."""
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found."}), 404

    return jsonify({
        "success": True,
        "complaint_id": complaint_id,
        "history": [h.to_dict() for h in complaint.status_history]
    }), 200
