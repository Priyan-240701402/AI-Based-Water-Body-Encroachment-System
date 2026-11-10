"""
Water Bodies API Blueprint.
Endpoints to fetch catalog of mapped water bodies with GeoJSON boundaries.
"""

from flask import Blueprint, jsonify
from backend.database import db
from backend.models.water_body import WaterBody

water_body_bp = Blueprint("water_body_api", __name__, url_prefix="/api/water-bodies")

@water_body_bp.route("", methods=["GET"])
def get_water_bodies():
    """Returns all mapped water bodies."""
    water_bodies = WaterBody.query.all()
    return jsonify({
        "success": True,
        "count": len(water_bodies),
        "water_bodies": [wb.to_dict() for wb in water_bodies]
    }), 200

@water_body_bp.route("/<int:wb_id>", methods=["GET"])
def get_water_body(wb_id: int):
    """Returns single water body details."""
    wb = db.session.get(WaterBody, wb_id)
    if not wb:
        return jsonify({"success": False, "message": "Water body not found."}), 404
    return jsonify({"success": True, "water_body": wb.to_dict()}), 200
