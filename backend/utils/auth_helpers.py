"""
Authentication and Authorization Helpers.
Handles password security and strict role-based access control (RBAC).
Validates user roles against PostgreSQL database records.
"""

from functools import wraps
from flask import session, jsonify, redirect, url_for, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import db
from backend.models.user import User

def hash_password(password: str) -> str:
    """Hashes a plaintext password securely."""
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    """Verifies a plaintext password against stored hash."""
    return check_password_hash(password_hash, password)

def get_current_user():
    """Retrieves currently logged-in user directly from PostgreSQL database."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)

def get_role_redirect_url(role: str) -> str:
    """Returns the appropriate landing dashboard for a given user role."""
    role = (role or "").lower()
    if role in ("authority", "officer"):
        return url_for("web.officer_dashboard")
    elif role == "admin":
        return url_for("web.admin_dashboard")
    else:
        return url_for("web.citizen_dashboard")

def login_required(f):
    """Ensures user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            session.clear()
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Authentication required. Please log in."}), 401
            return redirect(url_for("web.login_page"))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """
    Strict server-side RBAC decorator.
    Validates authenticated user's role against database record.
    Allowed roles can include 'citizen', 'officer', 'authority', 'admin'.
    'officer' and 'authority' are treated as equivalent officer roles.
    'admin' is allowed everywhere for administrative oversight.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                session.clear()
                if request.path.startswith("/api/"):
                    return jsonify({"success": False, "message": "Authentication required. Please log in."}), 401
                return redirect(url_for("web.login_page"))
            
            user_role = (user.role or "").lower()

            # Normalize roles
            normalized_allowed = set(r.lower() for r in allowed_roles)
            if "officer" in normalized_allowed:
                normalized_allowed.add("authority")
            if "authority" in normalized_allowed:
                normalized_allowed.add("officer")
            
            # Admin is always permitted
            normalized_allowed.add("admin")

            if user_role not in normalized_allowed:
                if request.path.startswith("/api/"):
                    return jsonify({"success": False, "message": "Forbidden. Access denied for your user role."}), 403
                return redirect(url_for("web.access_denied_page"))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def citizen_required(f):
    return role_required("citizen")(f)

def officer_required(f):
    return role_required("officer", "authority")(f)

def admin_required(f):
    return role_required("admin")(f)
