"""
Water Body Encroachment Complaint and Monitoring System.
Flask Application Entry Point and App Factory.
Registers role-based blueprints for Citizens, Officers, and Admins.
"""

import os
import sys
from pathlib import Path

# Always ensure working directory is the project root.
# This fixes route registration failures when running as:
#   python app.py         (from backend/ directory)
#   python backend/app.py (from project root)
project_root = str(Path(__file__).resolve().parent.parent)
if os.getcwd() != project_root:
    os.chdir(project_root)

# Ensure project root is in sys.path for absolute imports
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, jsonify
from backend.config import Config, config_by_name
from backend.database import init_db, db

def create_app(config_name: str = None) -> Flask:
    """Application factory for Flask."""
    base_dir = Path(__file__).resolve().parent.parent
    templates_dir = base_dir / "frontend" / "templates"
    static_dir = base_dir / "frontend" / "static"

    app = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir)
    )

    # Load configuration
    config_class = config_by_name.get(config_name or os.getenv("FLASK_ENV", "development"), Config)
    app.config.from_object(config_class)

    # Initialize PostgreSQL database with SQLAlchemy
    init_db(app)

    # Register Blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.complaint_routes import complaint_bp
    from backend.routes.ai_routes import ai_bp
    from backend.routes.water_body_routes import water_body_bp
    from backend.routes.authority_routes import authority_bp
    from backend.routes.web_routes import web_bp
    from backend.routes.citizen_routes import citizen_bp
    from backend.routes.officer_routes import officer_bp
    from backend.routes.admin_routes import admin_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(water_body_bp)
    app.register_blueprint(authority_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(officer_bp)
    app.register_blueprint(admin_bp)

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"success": False, "message": "The requested resource was not found."}), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({"success": False, "message": "An unexpected internal server error occurred."}), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    use_reloader = os.getenv("FLASK_USE_RELOADER", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=use_reloader)
