"""
Authorities API Blueprint.
Endpoints to list regulatory authorities and departments.
"""

from flask import Blueprint, jsonify
from backend.database import db
from backend.models.authority import Authority

authority_bp = Blueprint("authority_api", __name__, url_prefix="/api/authorities")

@authority_bp.route("", methods=["GET"])
def get_authorities():
    """Returns list of active authorities and jurisdiction info."""
    authorities = Authority.query.all()
    return jsonify({
        "success": True,
        "count": len(authorities),
        "authorities": [a.to_dict() for a in authorities]
    }), 200

@authority_bp.route("/<int:authority_id>", methods=["GET"])
def get_authority(authority_id: int):
    """Returns single authority details."""
    a = db.session.get(Authority, authority_id)
    if not a:
        return jsonify({"success": False, "message": "Authority not found."}), 404
    return jsonify({"success": True, "authority": a.to_dict()}), 200
