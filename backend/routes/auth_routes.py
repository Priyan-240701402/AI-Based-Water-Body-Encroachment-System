"""
Authentication API Blueprint.
Endpoints for user registration, login, logout, and current user profile.
Calculates server-side role redirect URLs.
"""

from flask import Blueprint, request, jsonify, session, url_for
from backend.database import db
from backend.models.user import User
from backend.utils.auth_helpers import hash_password, verify_password, get_current_user, get_role_redirect_url

auth_bp = Blueprint("auth_api", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    phone = data.get("phone", "").strip()
    role = data.get("role", "citizen").strip().lower()

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, and password are required."}), 400

    if role not in ("citizen", "authority", "officer"):
        role = "citizen"

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "An account with this email already exists."}), 409

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters long."}), 400

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        phone=phone
    )
    db.session.add(user)
    db.session.commit()

    # Log in user automatically upon registration
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_role"] = user.role

    redirect_url = get_role_redirect_url(user.role)

    return jsonify({
        "success": True,
        "message": "Registration successful.",
        "user": user.to_dict(),
        "redirect_url": redirect_url
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_role"] = user.role

    redirect_url = get_role_redirect_url(user.role)

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user": user.to_dict(),
        "redirect_url": redirect_url
    }), 200

@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."}), 200

@auth_bp.route("/me", methods=["GET"])
def me():
    user = get_current_user()
    if not user:
        return jsonify({"authenticated": False}), 200
    return jsonify({
        "authenticated": True,
        "user": user.to_dict(),
        "redirect_url": get_role_redirect_url(user.role)
    }), 200
