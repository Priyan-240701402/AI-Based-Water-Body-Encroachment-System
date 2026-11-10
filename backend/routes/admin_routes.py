"""
Admin Portal API Blueprint.
Endpoints for user management, officer configuration, authority management,
water bodies, complaint assignments, system analytics, and AI rule management.
Strictly enforced with admin_required decorator.
"""

from flask import Blueprint, jsonify, session, request
from backend.database import db
from backend.models.user import User
from backend.models.authority import Authority
from backend.models.water_body import WaterBody
from backend.models.complaint import Complaint
from backend.models.assignment import AuthorityAssignment
from backend.models.rule import Rule
from backend.services.complaint_service import ComplaintService
from backend.utils.auth_helpers import admin_required, hash_password, get_current_user
import json

admin_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")

@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def admin_dashboard_stats():
    complaints = Complaint.query.all()
    users = User.query.all()
    authorities = Authority.query.all()
    water_bodies = WaterBody.query.all()

    stats = {
        "total_complaints": len(complaints),
        "unassigned": sum(1 for c in complaints if not c.assignments),
        "pending": sum(1 for c in complaints if c.status in ("SUBMITTED", "AI_REVIEWED")),
        "high_priority": sum(1 for c in complaints if c.priority in ("HIGH", "CRITICAL")),
        "resolved": sum(1 for c in complaints if c.status == "RESOLVED"),
        "total_citizens": sum(1 for u in users if u.role == "citizen"),
        "total_officers": sum(1 for u in users if u.role in ("authority", "officer")),
        "total_authorities": len(authorities),
        "total_water_bodies": len(water_bodies)
    }
    return jsonify({"success": True, "stats": stats}), 200

# -------------------------------------------------------------------
# USER MANAGEMENT APIs
# -------------------------------------------------------------------
@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    role_filter = request.args.get("role")
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter.lower())
    users = query.order_by(User.created_at.desc()).all()
    return jsonify({"success": True, "count": len(users), "users": [u.to_dict() for u in users]}), 200

# -------------------------------------------------------------------
# OFFICER MANAGEMENT APIs
# -------------------------------------------------------------------
@admin_bp.route("/officers", methods=["GET"])
@admin_required
def list_officers():
    officers = User.query.filter(User.role.in_(["authority", "officer"])).all()
    officer_list = []
    for off in officers:
        data = off.to_dict()
        # Find matching authority record by email if present
        auth = Authority.query.filter_by(email=off.email).first()
        if auth:
            data["authority"] = auth.to_dict()
            # Calculate active workload from assignment table
            active_cases = AuthorityAssignment.query.filter_by(authority_id=auth.id).count()
            data["active_workload"] = active_cases
            data["max_active_cases"] = auth.max_active_cases
        else:
            data["active_workload"] = 0
            data["max_active_cases"] = 20
        officer_list.append(data)
    return jsonify({"success": True, "officers": officer_list}), 200

@admin_bp.route("/officers", methods=["POST"])
@admin_required
def create_officer():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "Password@123")
    department = data.get("department", "REVENUE").strip().upper()
    jurisdiction = data.get("jurisdiction", "Central Zone").strip()
    phone = data.get("phone", "").strip()
    max_cases = int(data.get("max_active_cases", 20))

    if not name or not email:
        return jsonify({"success": False, "message": "Officer name and email are required."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "An account with this email already exists."}), 409

    # Create User account with officer/authority role
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="authority",
        phone=phone
    )
    db.session.add(user)

    # Create Authority record
    auth = Authority(
        name=f"{jurisdiction} {department.capitalize()} Office ({name})",
        department=department,
        jurisdiction=jurisdiction,
        email=email,
        contact=phone,
        status="ACTIVE",
        max_active_cases=max_cases
    )
    db.session.add(auth)
    db.session.commit()

    return jsonify({"success": True, "message": "Officer account and authority profile created.", "officer": user.to_dict()}), 201

# -------------------------------------------------------------------
# AUTHORITY MANAGEMENT APIs
# -------------------------------------------------------------------
@admin_bp.route("/authorities", methods=["GET"])
@admin_required
def list_authorities():
    authorities = Authority.query.order_by(Authority.id.asc()).all()
    return jsonify({"success": True, "count": len(authorities), "authorities": [a.to_dict() for a in authorities]}), 200

@admin_bp.route("/authorities", methods=["POST"])
@admin_required
def create_authority():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    department = data.get("department", "MUNICIPAL").strip().upper()
    jurisdiction = data.get("jurisdiction", "Central Zone").strip()
    email = data.get("email", "").strip()
    contact = data.get("contact", "").strip()
    max_cases = int(data.get("max_active_cases", 20))

    if not name or not department or not jurisdiction:
        return jsonify({"success": False, "message": "Name, department, and jurisdiction are required."}), 400

    auth = Authority(
        name=name,
        department=department,
        jurisdiction=jurisdiction,
        email=email,
        contact=contact,
        status="ACTIVE",
        max_active_cases=max_cases
    )
    db.session.add(auth)
    db.session.commit()
    return jsonify({"success": True, "message": "Authority record created.", "authority": auth.to_dict()}), 201

@admin_bp.route("/authorities/<int:auth_id>", methods=["PUT"])
@admin_required
def update_authority(auth_id: int):
    auth = db.session.get(Authority, auth_id)
    if not auth:
        return jsonify({"success": False, "message": "Authority not found."}), 404
    data = request.get_json() or {}
    if "name" in data: auth.name = data["name"].strip()
    if "department" in data: auth.department = data["department"].strip().upper()
    if "jurisdiction" in data: auth.jurisdiction = data["jurisdiction"].strip()
    if "status" in data: auth.status = data["status"].strip().upper()
    if "max_active_cases" in data: auth.max_active_cases = int(data["max_active_cases"])
    db.session.commit()
    return jsonify({"success": True, "message": "Authority updated.", "authority": auth.to_dict()}), 200

# -------------------------------------------------------------------
# WATER-BODY MANAGEMENT APIs
# -------------------------------------------------------------------
@admin_bp.route("/water-bodies", methods=["GET"])
@admin_required
def list_water_bodies():
    bodies = WaterBody.query.order_by(WaterBody.name.asc()).all()
    return jsonify({"success": True, "count": len(bodies), "water_bodies": [wb.to_dict() for wb in bodies]}), 200

@admin_bp.route("/water-bodies", methods=["POST"])
@admin_required
def create_water_body():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    wb_type = data.get("type", "LAKE").strip().upper()
    district = data.get("district", "Central Zone").strip()
    lat = float(data.get("center_latitude", 12.9716))
    lng = float(data.get("center_longitude", 77.5946))
    boundary_data = data.get("boundary_data")

    if not name:
        return jsonify({"success": False, "message": "Water body name is required."}), 400

    wb = WaterBody(
        name=name,
        type=wb_type,
        district=district,
        center_latitude=lat,
        center_longitude=lng,
        status="PROTECTED",
        boundary_data=json.dumps(boundary_data) if isinstance(boundary_data, dict) else boundary_data
    )
    db.session.add(wb)
    db.session.commit()
    return jsonify({"success": True, "message": "Water body record created.", "water_body": wb.to_dict()}), 201

# -------------------------------------------------------------------
# COMPLAINT ASSIGNMENTS APIs
# -------------------------------------------------------------------
@admin_bp.route("/assignments", methods=["GET"])
@admin_required
def list_assignments():
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    unassigned = [c.to_dict() for c in complaints if not c.assignments]
    assigned = [c.to_dict() for c in complaints if c.assignments]
    return jsonify({"success": True, "unassigned_count": len(unassigned), "assigned_count": len(assigned), "unassigned": unassigned, "assigned": assigned}), 200

@admin_bp.route("/assignments/auto", methods=["POST"])
@admin_required
def run_auto_assignments():
    unassigned = Complaint.query.filter(~Complaint.assignments.any()).all()
    assigned_count = 0
    failed_count = 0

    for c in unassigned:
        csp_res = ComplaintService.assign_authority_csp(c, c.water_body)
        if csp_res.get("success"):
            auth_data = csp_res["assigned_authority"]
            existing = AuthorityAssignment.query.filter_by(complaint_id=c.id).first()
            if not existing:
                assign = AuthorityAssignment(
                    complaint_id=c.id,
                    authority_id=auth_data["id"],
                    assigned_by="ADMIN_CSP_SYSTEM",
                    assignment_reason=csp_res.get("assignment_reason", "CSP Auto Assignment")
                )
                db.session.add(assign)
                c.status = "ASSIGNED"
                assigned_count += 1
        else:
            failed_count += 1

    db.session.commit()
    return jsonify({"success": True, "message": f"Auto-assignment complete. Assigned: {assigned_count}, Unassigned remaining: {failed_count}"}), 200

@admin_bp.route("/assignments/manual", methods=["POST"])
@admin_required
def manual_assign():
    data = request.get_json() or {}
    complaint_id = int(data.get("complaint_id", 0))
    authority_id = int(data.get("authority_id", 0))
    reason = data.get("reason", "Manual assignment by Administrator").strip()

    complaint = db.session.get(Complaint, complaint_id)
    authority = db.session.get(Authority, authority_id)

    if not complaint or not authority:
        return jsonify({"success": False, "message": "Invalid complaint or authority ID."}), 400

    existing = AuthorityAssignment.query.filter_by(complaint_id=complaint.id).first()
    if existing:
        existing.authority_id = authority.id
        existing.assignment_reason = reason
        existing.assigned_by = "ADMIN_MANUAL"
    else:
        new_assign = AuthorityAssignment(
            complaint_id=complaint.id,
            authority_id=authority.id,
            assigned_by="ADMIN_MANUAL",
            assignment_reason=reason
        )
        db.session.add(new_assign)

    complaint.status = "ASSIGNED"
    db.session.commit()

    return jsonify({"success": True, "message": f"Assigned complaint #{complaint_id} to {authority.name}."}), 200

# -------------------------------------------------------------------
# REPORTS & AI RULES APIs
# -------------------------------------------------------------------
@admin_bp.route("/reports", methods=["GET"])
@admin_required
def get_reports():
    complaints = Complaint.query.all()
    by_status = {}
    by_priority = {}
    by_district = {}

    for c in complaints:
        st = c.status
        pr = c.priority
        dist = c.water_body.district if c.water_body else "Central Zone"

        by_status[st] = by_status.get(st, 0) + 1
        by_priority[pr] = by_priority.get(pr, 0) + 1
        by_district[dist] = by_district.get(dist, 0) + 1

    return jsonify({
        "success": True,
        "total_complaints": len(complaints),
        "by_status": by_status,
        "by_priority": by_priority,
        "by_district": by_district
    }), 200

@admin_bp.route("/ai-rules", methods=["GET"])
@admin_required
def list_ai_rules():
    rules = Rule.query.order_by(Rule.priority.asc()).all()
    return jsonify({"success": True, "rules": [r.to_dict() for r in rules]}), 200

@admin_bp.route("/ai-rules/<int:rule_id>", methods=["PUT"])
@admin_required
def toggle_ai_rule(rule_id: int):
    rule = db.session.get(Rule, rule_id)
    if not rule:
        return jsonify({"success": False, "message": "Rule not found."}), 404
    data = request.get_json() or {}
    if "active" in data:
        rule.active = bool(data["active"])
    db.session.commit()
    return jsonify({"success": True, "message": f"Rule {rule.rule_name} active state updated to {rule.active}.", "rule": rule.to_dict()}), 200
