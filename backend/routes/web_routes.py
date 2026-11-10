"""
Web UI Routes Blueprint.
Renders Jinja2 HTML templates for Citizens, Officers, and Administrators.
Enforces strict server-side Role-Based Access Control (RBAC).
"""

from flask import Blueprint, render_template, send_from_directory, current_app, session, redirect, url_for, abort, request
from backend.database import db
from backend.models.complaint import Complaint
from backend.models.water_body import WaterBody
from backend.models.authority import Authority
from backend.models.user import User
from backend.models.assignment import AuthorityAssignment
from backend.models.rule import Rule
from backend.models.history import ComplaintStatusHistory
from backend.utils.auth_helpers import (
    get_current_user,
    login_required,
    citizen_required,
    officer_required,
    admin_required,
    get_role_redirect_url
)

web_bp = Blueprint("web", __name__)

# ===================================================================
# PUBLIC & COMMON ROUTES
# ===================================================================

@web_bp.route("/")
def index():
    user = get_current_user()
    return render_template("index.html", user=user)

@web_bp.route("/login")
def login_page():
    user = get_current_user()
    if user:
        return redirect(get_role_redirect_url(user.role))
    return render_template("login.html")

@web_bp.route("/register")
def register_page():
    user = get_current_user()
    if user:
        return redirect(get_role_redirect_url(user.role))
    return render_template("register.html")

@web_bp.route("/access-denied")
def access_denied_page():
    user = get_current_user()
    return render_template("access_denied.html", user=user), 403

# ===================================================================
# CITIZEN PORTAL ROUTES
# ===================================================================

@web_bp.route("/citizen/dashboard")
@citizen_required
def citizen_dashboard():
    user = get_current_user()
    complaints = Complaint.query.filter_by(user_id=user.id).order_by(Complaint.created_at.desc()).all()
    stats = {
        "total": len(complaints),
        "pending": sum(1 for c in complaints if c.status in ("SUBMITTED", "AI_REVIEWED")),
        "under_verification": sum(1 for c in complaints if c.status in ("ASSIGNED", "UNDER_VERIFICATION", "ACTION_REQUIRED")),
        "resolved": sum(1 for c in complaints if c.status == "RESOLVED")
    }
    return render_template("citizen/dashboard.html", user=user, complaints=complaints, stats=stats)

@web_bp.route("/citizen/complaints/new")
@citizen_required
def new_complaint():
    user = get_current_user()
    water_bodies = WaterBody.query.all()
    return render_template("citizen/new_complaint.html", user=user, water_bodies=water_bodies)

@web_bp.route("/citizen/complaints")
@citizen_required
def citizen_complaints_list():
    user = get_current_user()
    complaints = Complaint.query.filter_by(user_id=user.id).order_by(Complaint.created_at.desc()).all()
    return render_template("citizen/complaints_list.html", user=user, complaints=complaints)

@web_bp.route("/citizen/complaints/<int:complaint_id>")
@citizen_required
def citizen_complaint_detail(complaint_id: int):
    user = get_current_user()
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        abort(404)
    # Ownership Check: Citizens can only view their own complaints
    if complaint.user_id != user.id and user.role != "admin":
        return redirect(url_for("web.access_denied_page"))
    return render_template("citizen/complaint_detail.html", user=user, complaint=complaint)

@web_bp.route("/citizen/profile")
@citizen_required
def citizen_profile():
    user = get_current_user()
    return render_template("citizen/profile.html", user=user)

# ===================================================================
# OFFICER PORTAL ROUTES
# ===================================================================

@web_bp.route("/officer/dashboard")
@officer_required
def officer_dashboard():
    user = get_current_user()
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    stats = {
        "total": len(complaints),
        "pending": sum(1 for c in complaints if c.status in ("SUBMITTED", "AI_REVIEWED")),
        "under_verification": sum(1 for c in complaints if c.status in ("ASSIGNED", "UNDER_VERIFICATION")),
        "high_priority": sum(1 for c in complaints if c.priority in ("HIGH", "CRITICAL")),
        "action_required": sum(1 for c in complaints if c.status == "ACTION_REQUIRED"),
        "resolved": sum(1 for c in complaints if c.status == "RESOLVED")
    }
    return render_template("officer/dashboard.html", user=user, complaints=complaints, stats=stats)

@web_bp.route("/officer/complaints")
@officer_required
def officer_complaints():
    user = get_current_user()
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    water_bodies = WaterBody.query.all()
    authorities = Authority.query.all()
    return render_template("officer/complaints.html", user=user, complaints=complaints, water_bodies=water_bodies, authorities=authorities)

@web_bp.route("/officer/complaints/<int:complaint_id>")
@officer_required
def officer_complaint_detail(complaint_id: int):
    return redirect(url_for("web.officer_complaint_verify", complaint_id=complaint_id))

@web_bp.route("/officer/complaints/<int:complaint_id>/verify")
@officer_required
def officer_complaint_verify(complaint_id: int):
    user = get_current_user()
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        abort(404)
    authorities = Authority.query.all()
    return render_template("officer/verify_complaint.html", user=user, complaint=complaint, authorities=authorities)

@web_bp.route("/officer/map")
@officer_required
def officer_map():
    user = get_current_user()
    return render_template("officer/map.html", user=user)

@web_bp.route("/officer/inspections")
@officer_required
def officer_inspections():
    user = get_current_user()
    history = ComplaintStatusHistory.query.order_by(ComplaintStatusHistory.changed_at.desc()).all()
    return render_template("officer/inspections.html", user=user, history=history)

@web_bp.route("/officer/profile")
@officer_required
def officer_profile():
    user = get_current_user()
    return render_template("officer/profile.html", user=user)

# ===================================================================
# ADMIN PORTAL ROUTES
# ===================================================================

@web_bp.route("/admin/dashboard")
@officer_required  # Permits authority, officer, and admin
def admin_dashboard():
    user = get_current_user()
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
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
    return render_template("admin/dashboard.html", user=user, complaints=complaints, stats=stats)

@web_bp.route("/admin/users")
@admin_required
def admin_users():
    user = get_current_user()
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", user=user, users=users)

@web_bp.route("/admin/officers")
@admin_required
def admin_officers():
    user = get_current_user()
    officers = User.query.filter(User.role.in_(["authority", "officer"])).all()
    authorities = Authority.query.all()
    return render_template("admin/officers.html", user=user, officers=officers, authorities=authorities)

@web_bp.route("/admin/authorities")
@admin_required
def admin_authorities():
    user = get_current_user()
    authorities = Authority.query.order_by(Authority.id.asc()).all()
    return render_template("admin/authorities.html", user=user, authorities=authorities)

@web_bp.route("/admin/water-bodies")
@admin_required
def admin_water_bodies():
    user = get_current_user()
    water_bodies = WaterBody.query.order_by(WaterBody.name.asc()).all()
    return render_template("admin/water_bodies.html", user=user, water_bodies=water_bodies)

@web_bp.route("/admin/assignments")
@admin_required
def admin_assignments():
    user = get_current_user()
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    authorities = Authority.query.all()
    return render_template("admin/assignments.html", user=user, complaints=complaints, authorities=authorities)

@web_bp.route("/admin/map")
@officer_required  # Permits authority, officer, and admin
def admin_map():
    user = get_current_user()
    return render_template("admin/map.html", user=user)

@web_bp.route("/admin/reports")
@admin_required
def admin_reports():
    user = get_current_user()
    complaints = Complaint.query.all()
    water_bodies = WaterBody.query.all()
    authorities = Authority.query.all()
    return render_template("admin/reports.html", user=user, complaints=complaints, water_bodies=water_bodies, authorities=authorities)

@web_bp.route("/admin/ai-rules")
@admin_required
def admin_ai_rules():
    user = get_current_user()
    rules = Rule.query.order_by(Rule.priority.asc()).all()
    return render_template("admin/ai_rules.html", user=user, rules=rules)

@web_bp.route("/admin/audit-logs")
@admin_required
def admin_audit_logs():
    user = get_current_user()
    history = ComplaintStatusHistory.query.order_by(ComplaintStatusHistory.changed_at.desc()).all()
    return render_template("admin/audit_logs.html", user=user, history=history)

# Legacy alias for existing tests/links
@web_bp.route("/admin/complaints/<int:complaint_id>")
@officer_required
def admin_complaint_verify(complaint_id: int):
    return redirect(url_for("web.officer_complaint_verify", complaint_id=complaint_id))

@web_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serves uploaded evidence files securely."""
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "backend/uploads")
    return send_from_directory(upload_dir, filename)
