import os
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()

def init_db(app):
    """
    Initializes the database connection with SQLAlchemy.
    Primary database: PostgreSQL via psycopg.
    Tests PostgreSQL connection first; if credentials fail or service is unreachable,
    falls back to local SQLite to ensure uninterrupted local execution.
    """
    primary_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    
    # Check if primary connection is PostgreSQL
    if primary_uri.startswith("postgresql"):
        try:
            logger.info("Attempting connection to primary PostgreSQL database...")
            test_engine = create_engine(primary_uri, pool_pre_ping=True)
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            test_engine.dispose()
            logger.info("Successfully connected to PostgreSQL database via psycopg.")
        except Exception as err:
            logger.warning(
                f"PostgreSQL connection failed ({err}). "
                "Switching to local SQLite fallback database for uninterrupted execution."
            )
            os.makedirs(app.instance_path, exist_ok=True)
            db_path = os.path.join(app.instance_path, "water_body_encroachment.db")
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    db.init_app(app)

    with app.app_context():
        # Ensure all models are loaded before creating tables
        from backend import models  # noqa: F401
        db.create_all()
        logger.info(f"Database tables verified using {app.config['SQLALCHEMY_DATABASE_URI'].split('://')[0]}.")
        
        # Seed initial demo data if empty
        seed_default_data()

def seed_default_data():
    """Seeds default demo users, water bodies, authorities, and AI rules if not present."""
    from backend.models.user import User
    from backend.models.water_body import WaterBody
    from backend.models.authority import Authority
    from backend.models.rule import Rule
    from werkzeug.security import generate_password_hash
    import json

    try:
        # 1. Seed Users
        if User.query.count() == 0:
            pw_hash = generate_password_hash("Password@123")
            demo_users = [
                User(name="System Administrator", email="admin@waterbodies.gov.in", password_hash=pw_hash, role="admin", phone="+91-9876543210"),
                User(name="Chief Revenue Officer Ramesh Kumar", email="officer.revenue@waterbodies.gov.in", password_hash=pw_hash, role="authority", phone="+91-9876543211"),
                User(name="Municipal Engineer Priya Sharma", email="officer.municipal@waterbodies.gov.in", password_hash=pw_hash, role="authority", phone="+91-9876543212"),
                User(name="Water Resources Executive Ananya Roy", email="officer.water@waterbodies.gov.in", password_hash=pw_hash, role="authority", phone="+91-9876543213"),
                User(name="Demo Citizen Ravi", email="citizen@example.com", password_hash=pw_hash, role="citizen", phone="+91-9876500001"),
            ]
            db.session.add_all(demo_users)
            db.session.commit()
            logger.info("Demo users seeded successfully.")

        # 2. Seed Water Bodies
        if WaterBody.query.count() == 0:
            demo_water_bodies = [
                WaterBody(
                    name="Bellandur Lake",
                    type="LAKE",
                    district="East Zone",
                    boundary_data=json.dumps({"type": "Polygon", "coordinates": [[[77.660, 12.930], [77.685, 12.930], [77.685, 12.945], [77.660, 12.945], [77.660, 12.930]]]}),
                    status="CRITICAL",
                    center_latitude=12.9375,
                    center_longitude=77.6725
                ),
                WaterBody(
                    name="Sankey Tank",
                    type="POND",
                    district="North Zone",
                    boundary_data=json.dumps({"type": "Polygon", "coordinates": [[[77.568, 13.004], [77.575, 13.004], [77.575, 13.012], [77.568, 13.012], [77.568, 13.004]]]}),
                    status="PROTECTED",
                    center_latitude=13.0080,
                    center_longitude=77.5715
                ),
                WaterBody(
                    name="Varthur Lake",
                    type="LAKE",
                    district="East Zone",
                    boundary_data=json.dumps({"type": "Polygon", "coordinates": [[[77.730, 12.940], [77.755, 12.940], [77.755, 12.960], [77.730, 12.960], [77.730, 12.940]]]}),
                    status="UNDER_THREAT",
                    center_latitude=12.9500,
                    center_longitude=77.7425
                ),
                WaterBody(
                    name="Rajakaluve Main Canal",
                    type="CANAL",
                    district="Central Zone",
                    boundary_data=json.dumps({"type": "LineString", "coordinates": [[77.600, 12.965], [77.620, 12.970], [77.640, 12.975]]}),
                    status="UNDER_THREAT",
                    center_latitude=12.9700,
                    center_longitude=77.6200
                ),
                WaterBody(
                    name="Ulsoor Lake",
                    type="LAKE",
                    district="Central Zone",
                    boundary_data=json.dumps({"type": "Polygon", "coordinates": [[[77.618, 12.980], [77.628, 12.980], [77.628, 12.989], [77.618, 12.989], [77.618, 12.980]]]}),
                    status="PROTECTED",
                    center_latitude=12.9845,
                    center_longitude=77.6230
                ),
            ]
            db.session.add_all(demo_water_bodies)
            db.session.commit()
            logger.info("Demo water bodies seeded successfully.")

        # 3. Seed Authorities
        if Authority.query.count() == 0:
            demo_authorities = [
                Authority(name="North Zone Municipal Encroachment Cell", department="MUNICIPAL", jurisdiction="North Zone", contact="+91-80-22220001", email="north.municipal@waterbodies.gov.in", status="ACTIVE", max_active_cases=15),
                Authority(name="East Zone Municipal Water Directorate", department="MUNICIPAL", jurisdiction="East Zone", contact="+91-80-22220002", email="east.municipal@waterbodies.gov.in", status="ACTIVE", max_active_cases=20),
                Authority(name="Central Zone Revenue & Survey Department", department="REVENUE", jurisdiction="Central Zone", contact="+91-80-22220003", email="central.revenue@waterbodies.gov.in", status="ACTIVE", max_active_cases=12),
                Authority(name="East Zone Revenue & Survey Office", department="REVENUE", jurisdiction="East Zone", contact="+91-80-22220004", email="east.revenue@waterbodies.gov.in", status="ACTIVE", max_active_cases=18),
                Authority(name="State Water Resources Department (Lakes & Canals)", department="WATER_RESOURCES", jurisdiction="East Zone", contact="+91-80-22220005", email="wrd.east@waterbodies.gov.in", status="ACTIVE", max_active_cases=25),
                Authority(name="State Water Resources Department (Central)", department="WATER_RESOURCES", jurisdiction="Central Zone", contact="+91-80-22220006", email="wrd.central@waterbodies.gov.in", status="ACTIVE", max_active_cases=25),
                Authority(name="State Pollution Control & Wetland Authority", department="ENVIRONMENTAL", jurisdiction="North Zone", contact="+91-80-22220007", email="env.north@waterbodies.gov.in", status="ACTIVE", max_active_cases=10),
            ]
            db.session.add_all(demo_authorities)
            db.session.commit()
            logger.info("Demo authorities seeded successfully.")

        # 4. Seed Rules
        if Rule.query.count() == 0:
            demo_rules = [
                Rule(
                    rule_name="R001_CONSTRUCTION_INSIDE_BOUNDARY",
                    description="Construction activity inside or abutting mapped boundary indicates possible encroachment",
                    conditions={"has_construction": True, "inside_boundary": True},
                    conclusion="POSSIBLE_ENCROACHMENT",
                    priority=1,
                    active=True
                ),
                Rule(
                    rule_name="R002_NO_PERMISSION_VERIFICATION",
                    description="Possible encroachment without verified permission warrants official field verification",
                    conditions={"POSSIBLE_ENCROACHMENT": True, "has_permission": False},
                    conclusion="REQUIRES_OFFICIAL_VERIFICATION",
                    priority=2,
                    active=True
                ),
                Rule(
                    rule_name="R003_HIGH_IMPACT_PRIORITY",
                    description="Encroachment in protected lake or high affected area elevates priority to HIGH",
                    conditions={"REQUIRES_OFFICIAL_VERIFICATION": True, "affected_area_level": "HIGH"},
                    conclusion="PRIORITY_HIGH",
                    priority=3,
                    active=True
                ),
                Rule(
                    rule_name="R004_CANAL_FLOW_OBSTRUCTION",
                    description="Any construction along canal path raises immediate critical water flow threat",
                    conditions={"water_body_type": "CANAL", "has_construction": True},
                    conclusion="FLOW_OBSTRUCTION_RISK",
                    priority=2,
                    active=True
                ),
                Rule(
                    rule_name="R005_INSUFFICIENT_EVIDENCE",
                    description="Complaint lacking location boundary match or clear evidence flags insufficient information",
                    conditions={"inside_boundary": False, "has_construction": False},
                    conclusion="NO_PRELIMINARY_INDICATOR",
                    priority=1,
                    active=True
                )
            ]
            db.session.add_all(demo_rules)
            db.session.commit()
            logger.info("Demo rules seeded successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding initial data: {e}")
