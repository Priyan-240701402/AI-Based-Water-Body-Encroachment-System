"""
Comprehensive Seed Script for Water Body Encroachment Complaint System.

Creates realistic, interconnected demo data using the actual SQLAlchemy models
and AI reasoning engines. Idempotent — safe to re-run.

Usage:
    python database/seed_demo.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Ensure project root is on path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# ──────────────────────────────────────────────────────────────
# 1.  Boot Flask application context
# ──────────────────────────────────────────────────────────────
from backend.app import create_app
from backend.database import db
from backend.models.user import User
from backend.models.water_body import WaterBody
from backend.models.authority import Authority
from backend.models.rule import Rule
from backend.models.complaint import Complaint
from backend.models.evidence import ComplaintEvidence
from backend.models.assignment import AuthorityAssignment
from backend.models.history import ComplaintStatusHistory
from backend.ai.knowledge_base import KnowledgeBase
from backend.ai.forward_chaining import ForwardChainingEngine
from backend.ai.csp import AuthorityCSP
from backend.services.map_service import MapService
from werkzeug.security import generate_password_hash

app = create_app()

# ──────────────────────────────────────────────────────────────
# 2.  Helper Utilities
# ──────────────────────────────────────────────────────────────
NOW = datetime.now(timezone.utc)
def ts(days_ago: int = 0, hours_ago: int = 0) -> datetime:
    """Returns a timestamp in the past."""
    return NOW - timedelta(days=days_ago, hours=hours_ago)

PW_HASH = generate_password_hash("Password@123")

# ──────────────────────────────────────────────────────────────
# 3.  SEED DATA DEFINITIONS
# ──────────────────────────────────────────────────────────────

USERS = [
    # Admin
    dict(name="System Administrator", email="admin@waterbodies.gov.in", role="admin", phone="+91-9876543210"),
    # Authorities
    dict(name="Chief Revenue Officer Ramesh Kumar", email="officer.revenue@waterbodies.gov.in", role="authority", phone="+91-9876543211"),
    dict(name="Municipal Engineer Priya Sharma", email="officer.municipal@waterbodies.gov.in", role="authority", phone="+91-9876543212"),
    dict(name="Water Resources Executive Ananya Roy", email="officer.water@waterbodies.gov.in", role="authority", phone="+91-9876543213"),
    # Citizens
    dict(name="Ravi Kumar", email="citizen1@example.com", role="citizen", phone="+91-9876500001"),
    dict(name="Sneha Patil", email="citizen2@example.com", role="citizen", phone="+91-9876500002"),
    dict(name="Arjun Reddy", email="citizen3@example.com", role="citizen", phone="+91-9876500003"),
    dict(name="Meera Nair", email="citizen4@example.com", role="citizen", phone="+91-9876500004"),
    dict(name="Vikram Singh", email="citizen5@example.com", role="citizen", phone="+91-9876500005"),
]

WATER_BODIES = [
    dict(name="Demo Bellandur Lake", type="LAKE", district="East Zone",
         boundary_data='{"type":"Polygon","coordinates":[[[77.660,12.930],[77.685,12.930],[77.685,12.945],[77.660,12.945],[77.660,12.930]]]}',
         status="CRITICAL", center_latitude=12.9375, center_longitude=77.6725),
    dict(name="Demo Sankey Tank", type="POND", district="North Zone",
         boundary_data='{"type":"Polygon","coordinates":[[[77.568,13.004],[77.575,13.004],[77.575,13.012],[77.568,13.012],[77.568,13.004]]]}',
         status="PROTECTED", center_latitude=13.0080, center_longitude=77.5715),
    dict(name="Demo Varthur Lake", type="LAKE", district="East Zone",
         boundary_data='{"type":"Polygon","coordinates":[[[77.730,12.940],[77.755,12.940],[77.755,12.960],[77.730,12.960],[77.730,12.940]]]}',
         status="UNDER_THREAT", center_latitude=12.9500, center_longitude=77.7425),
    dict(name="Demo Rajakaluve Main Canal", type="CANAL", district="Central Zone",
         boundary_data='{"type":"LineString","coordinates":[[77.600,12.965],[77.620,12.970],[77.640,12.975]]}',
         status="UNDER_THREAT", center_latitude=12.9700, center_longitude=77.6200),
    dict(name="Demo Ulsoor Lake", type="LAKE", district="Central Zone",
         boundary_data='{"type":"Polygon","coordinates":[[[77.618,12.980],[77.628,12.980],[77.628,12.989],[77.618,12.989],[77.618,12.980]]]}',
         status="PROTECTED", center_latitude=12.9845, center_longitude=77.6230),
    dict(name="Demo Hebbal Lake", type="LAKE", district="North Zone",
         boundary_data='{"type":"Polygon","coordinates":[[[77.585,13.040],[77.599,13.040],[77.599,13.052],[77.585,13.052],[77.585,13.040]]]}',
         status="PROTECTED", center_latitude=13.0460, center_longitude=77.5920),
    dict(name="Demo Agara Lake", type="LAKE", district="East Zone",
         boundary_data='{"type":"Polygon","coordinates":[[[77.630,12.920],[77.645,12.920],[77.645,12.935],[77.630,12.935],[77.630,12.920]]]}',
         status="UNDER_THREAT", center_latitude=12.9275, center_longitude=77.6375),
    dict(name="Demo Arkavathy River", type="RIVER", district="North Zone",
         boundary_data='{"type":"LineString","coordinates":[[77.520,13.060],[77.540,13.055],[77.560,13.050],[77.580,13.045]]}',
         status="PROTECTED", center_latitude=13.0525, center_longitude=77.5500),
    dict(name="Demo Madiwala Lake", type="LAKE", district="Central Zone",
         boundary_data='{"type":"Polygon","coordinates":[[[77.610,12.920],[77.625,12.920],[77.625,12.932],[77.610,12.932],[77.610,12.920]]]}',
         status="UNDER_THREAT", center_latitude=12.9260, center_longitude=77.6175),
    dict(name="Demo Yediyur Lake", type="POND", district="Central Zone",
         boundary_data='{"type":"Polygon","coordinates":[[[77.570,12.935],[77.580,12.935],[77.580,12.945],[77.570,12.945],[77.570,12.935]]]}',
         status="PROTECTED", center_latitude=12.9400, center_longitude=77.5750),
    dict(name="Demo Koramangala Canal", type="CANAL", district="East Zone",
         boundary_data='{"type":"LineString","coordinates":[[77.610,12.930],[77.630,12.935],[77.650,12.938]]}',
         status="CRITICAL", center_latitude=12.9340, center_longitude=77.6300),
    dict(name="Demo Jakkur Lake", type="LAKE", district="North Zone",
         boundary_data='{"type":"Polygon","coordinates":[[[77.600,13.070],[77.618,13.070],[77.618,13.082],[77.600,13.082],[77.600,13.070]]]}',
         status="PROTECTED", center_latitude=13.0760, center_longitude=77.6090),
]

AUTHORITIES = [
    dict(name="North Zone Municipal Encroachment Cell", department="MUNICIPAL", jurisdiction="North Zone",
         contact="+91-80-22220001", email="north.municipal@waterbodies.gov.in", status="ACTIVE", max_active_cases=15),
    dict(name="East Zone Municipal Water Directorate", department="MUNICIPAL", jurisdiction="East Zone",
         contact="+91-80-22220002", email="east.municipal@waterbodies.gov.in", status="ACTIVE", max_active_cases=20),
    dict(name="Central Zone Revenue & Survey Department", department="REVENUE", jurisdiction="Central Zone",
         contact="+91-80-22220003", email="central.revenue@waterbodies.gov.in", status="ACTIVE", max_active_cases=12),
    dict(name="East Zone Revenue & Survey Office", department="REVENUE", jurisdiction="East Zone",
         contact="+91-80-22220004", email="east.revenue@waterbodies.gov.in", status="ACTIVE", max_active_cases=18),
    dict(name="State Water Resources Dept (Lakes & Canals)", department="WATER_RESOURCES", jurisdiction="East Zone",
         contact="+91-80-22220005", email="wrd.east@waterbodies.gov.in", status="ACTIVE", max_active_cases=25),
    dict(name="State Water Resources Dept (Central)", department="WATER_RESOURCES", jurisdiction="Central Zone",
         contact="+91-80-22220006", email="wrd.central@waterbodies.gov.in", status="ACTIVE", max_active_cases=25),
    dict(name="State Pollution Control & Wetland Authority", department="ENVIRONMENTAL", jurisdiction="North Zone",
         contact="+91-80-22220007", email="env.north@waterbodies.gov.in", status="ACTIVE", max_active_cases=10),
    # INACTIVE authority (CSP must never assign to this)
    dict(name="Defunct South Zone Revenue Office", department="REVENUE", jurisdiction="East Zone",
         contact="+91-80-22220099", email="defunct@waterbodies.gov.in", status="INACTIVE", max_active_cases=5),
]

RULES = [
    dict(rule_name="R001_CONSTRUCTION_INSIDE_BOUNDARY",
         description="Construction activity inside or abutting mapped boundary indicates possible encroachment",
         conditions={"has_construction": True, "inside_boundary": True},
         conclusion="POSSIBLE_ENCROACHMENT", priority=1),
    dict(rule_name="R002_NO_PERMISSION_VERIFICATION",
         description="Possible encroachment without verified permission warrants official field verification",
         conditions={"POSSIBLE_ENCROACHMENT": True, "has_permission": False},
         conclusion="REQUIRES_OFFICIAL_VERIFICATION", priority=2),
    dict(rule_name="R003_HIGH_IMPACT_PRIORITY",
         description="Encroachment in protected lake or high affected area elevates priority to HIGH",
         conditions={"REQUIRES_OFFICIAL_VERIFICATION": True, "affected_area_level": "HIGH"},
         conclusion="PRIORITY_HIGH", priority=3),
    dict(rule_name="R004_CANAL_FLOW_OBSTRUCTION",
         description="Any construction along canal path raises immediate critical water flow threat",
         conditions={"water_body_type": "CANAL", "has_construction": True},
         conclusion="FLOW_OBSTRUCTION_RISK", priority=2),
    dict(rule_name="R005_PERMITTED_ACTIVITY",
         description="Activity with valid authorized permit is categorized as permitted",
         conditions={"has_construction": True, "has_permission": True},
         conclusion="PERMITTED_ACTIVITY", priority=2),
    dict(rule_name="R006_NO_INDICATOR",
         description="Reports with no physical construction and outside boundary have no preliminary indicators",
         conditions={"inside_boundary": False, "has_construction": False},
         conclusion="NO_PRELIMINARY_INDICATOR", priority=1),
    dict(rule_name="R007_RIVER_ENCROACHMENT",
         description="Construction near river bank inside boundary indicates possible encroachment",
         conditions={"water_body_type": "RIVER", "has_construction": True, "inside_boundary": True},
         conclusion="POSSIBLE_ENCROACHMENT", priority=1),
    dict(rule_name="R008_MEDIUM_PRIORITY",
         description="Verification required with medium affected area sets MEDIUM priority",
         conditions={"REQUIRES_OFFICIAL_VERIFICATION": True, "affected_area_level": "MEDIUM"},
         conclusion="PRIORITY_MEDIUM", priority=3),
]

# ──────────────────────────────────────────────────────────────
#  Demo Complaints — 22 carefully designed scenarios
#  Each has: title, description, water_body_index (0-based into WATER_BODIES),
#  citizen_index (0-based into citizen users: USERS[4..8]),
#  lat, lng, has_construction, has_permission, affected_area_level,
#  target_status (final status to drive lifecycle), days_ago
# ──────────────────────────────────────────────────────────────
COMPLAINTS = [
    # ── Scenario A: Clear encroachment, construction+boundary+no permission ──
    dict(title="Illegal wall near Bellandur Lake shore",
         description="A concrete wall is being constructed directly on the lake bund. No permission board visible. Workers active daily since last month.",
         wb_idx=0, citizen_idx=0, lat=12.935, lng=77.670,
         has_construction=True, has_permission=False, affected_area_level="HIGH",
         target_status="ASSIGNED", days_ago=14),

    dict(title="Multi-story building abutting Varthur Lake",
         description="Large 4-floor residential building under construction with foundation extending into lake area. No BBMP approval visible.",
         wb_idx=2, citizen_idx=1, lat=12.945, lng=77.740,
         has_construction=True, has_permission=False, affected_area_level="HIGH",
         target_status="UNDER_VERIFICATION", days_ago=21),

    dict(title="Compound wall blocking Agara Lake access",
         description="Private compound wall erected blocking public access path and extending into lake buffer zone.",
         wb_idx=6, citizen_idx=2, lat=12.928, lng=77.637,
         has_construction=True, has_permission=False, affected_area_level="MEDIUM",
         target_status="ACTION_REQUIRED", days_ago=30),

    # ── Scenario B: Construction OUTSIDE boundary ──
    dict(title="Building near Sankey Tank (outside boundary)",
         description="New building observed 500m from Sankey Tank. Construction appears to be on private land outside mapped boundary.",
         wb_idx=1, citizen_idx=3, lat=13.015, lng=77.580,
         has_construction=True, has_permission=False, affected_area_level="LOW",
         target_status="AI_REVIEWED", days_ago=5),

    dict(title="Shed construction away from Hebbal Lake",
         description="Metal shed erected approximately 400m from Hebbal Lake perimeter. Appears on private commercial land.",
         wb_idx=5, citizen_idx=4, lat=13.055, lng=77.600,
         has_construction=True, has_permission=False, affected_area_level="LOW",
         target_status="AI_REVIEWED", days_ago=3),

    # ── Scenario C: Construction WITH valid permission ──
    dict(title="Authorized BBMP drain repair at Ulsoor Lake",
         description="BBMP contractor performing authorized storm drain repair work. Permission board displayed at site with valid permit number.",
         wb_idx=4, citizen_idx=0, lat=12.984, lng=77.623,
         has_construction=True, has_permission=True, affected_area_level="LOW",
         target_status="RESOLVED", days_ago=45),

    dict(title="Government bridge repair near Madiwala Lake",
         description="PWD bridge repair work in progress with official notification and barricading. Authorized activity.",
         wb_idx=8, citizen_idx=1, lat=12.926, lng=77.618,
         has_construction=True, has_permission=True, affected_area_level="MEDIUM",
         target_status="RESOLVED", days_ago=60),

    # ── Scenario D: Canal obstruction (FLOW_OBSTRUCTION_RISK) ──
    dict(title="Debris dumped into Rajakaluve Canal",
         description="Large quantity of construction debris and garbage dumped into the canal channel, severely blocking water flow.",
         wb_idx=3, citizen_idx=2, lat=12.968, lng=77.615,
         has_construction=True, has_permission=False, affected_area_level="HIGH",
         target_status="ACTION_TAKEN", days_ago=35),

    dict(title="Concrete slab over Koramangala Canal",
         description="Illegal concrete slab laid across the canal to create vehicle access. Completely blocks natural water flow.",
         wb_idx=10, citizen_idx=3, lat=12.933, lng=77.625,
         has_construction=True, has_permission=False, affected_area_level="HIGH",
         target_status="ASSIGNED", days_ago=10),

    # ── Scenario E: Insufficient / missing information ──
    dict(title="Suspicious activity near Yediyur Lake",
         description="Saw some vehicles near the lake at night. Not sure what was happening. No photos taken.",
         wb_idx=9, citizen_idx=4, lat=12.950, lng=77.585,
         has_construction=False, has_permission=False, affected_area_level="LOW",
         target_status="SUBMITTED", days_ago=2),

    dict(title="Possible land filling near Jakkur Lake",
         description="Heard from neighbors that someone is filling land near the lake. Have not personally verified.",
         wb_idx=11, citizen_idx=0, lat=13.080, lng=77.615,
         has_construction=False, has_permission=False, affected_area_level="LOW",
         target_status="SUBMITTED", days_ago=1),

    # ── Scenario F: High priority encroachment ──
    dict(title="Massive commercial complex on Bellandur Lake bed",
         description="Large commercial complex foundation being laid directly on reclaimed lake bed. Heavy machinery operating 24/7. No permission boards anywhere.",
         wb_idx=0, citizen_idx=1, lat=12.938, lng=77.675,
         has_construction=True, has_permission=False, affected_area_level="HIGH",
         target_status="ACTION_REQUIRED", days_ago=18),

    dict(title="Unauthorized resort on Varthur Lake edge",
         description="Luxury resort construction with swimming pool directly encroaching into lake boundary. Massive environmental damage ongoing.",
         wb_idx=2, citizen_idx=2, lat=12.950, lng=77.742,
         has_construction=True, has_permission=False, affected_area_level="HIGH",
         target_status="UNDER_VERIFICATION", days_ago=25),

    # ── Various lifecycle stage complaints ──
    dict(title="Fencing inside Sankey Tank boundary",
         description="Barbed wire fencing erected inside the Sankey Tank park boundary. Restricting public access to lakefront.",
         wb_idx=1, citizen_idx=3, lat=13.007, lng=77.571,
         has_construction=True, has_permission=False, affected_area_level="MEDIUM",
         target_status="ASSIGNED", days_ago=12),

    dict(title="Encroachment resolved at Hebbal Lake",
         description="Previously reported illegal shed at Hebbal Lake has been demolished by authorities. Lake access restored.",
         wb_idx=5, citizen_idx=4, lat=13.046, lng=77.592,
         has_construction=True, has_permission=False, affected_area_level="MEDIUM",
         target_status="RESOLVED", days_ago=90),

    dict(title="Rejected duplicate complaint for Ulsoor area",
         description="Same issue already reported under complaint #3. This appears to be a duplicate submission by same citizen.",
         wb_idx=4, citizen_idx=0, lat=12.985, lng=77.625,
         has_construction=True, has_permission=False, affected_area_level="LOW",
         target_status="REJECTED", days_ago=40),

    dict(title="Parking lot encroaching Madiwala Lake buffer",
         description="Commercial parking lot constructed within 50m buffer zone of Madiwala Lake. Paved over with concrete.",
         wb_idx=8, citizen_idx=1, lat=12.927, lng=77.616,
         has_construction=True, has_permission=False, affected_area_level="MEDIUM",
         target_status="ASSIGNED", days_ago=8),

    dict(title="Construction on Arkavathy River floodplain",
         description="Housing colony being constructed on the Arkavathy River floodplain. During monsoon, this will block water flow and flood upstream areas.",
         wb_idx=7, citizen_idx=2, lat=13.053, lng=77.545,
         has_construction=True, has_permission=False, affected_area_level="HIGH",
         target_status="UNDER_VERIFICATION", days_ago=15),

    dict(title="Dumping waste near Agara Lake outlet",
         description="Municipal solid waste being dumped near the Agara Lake storm water outlet. Contaminating lake water.",
         wb_idx=6, citizen_idx=3, lat=12.925, lng=77.640,
         has_construction=True, has_permission=False, affected_area_level="MEDIUM",
         target_status="ACTION_TAKEN", days_ago=50),

    dict(title="Illegal borewell inside Jakkur Lake complex",
         description="Private borewell being drilled inside Jakkur Lake park complex without water authority permission.",
         wb_idx=11, citizen_idx=4, lat=13.076, lng=77.609,
         has_construction=True, has_permission=False, affected_area_level="MEDIUM",
         target_status="SUBMITTED", days_ago=1),

    dict(title="Godown on Yediyur Lake embankment",
         description="Large storage godown erected on Yediyur Lake embankment land. Structure appears permanent with RCC columns.",
         wb_idx=9, citizen_idx=0, lat=12.940, lng=77.575,
         has_construction=True, has_permission=False, affected_area_level="MEDIUM",
         target_status="AI_REVIEWED", days_ago=4),

    dict(title="Unauthorized pipe laid into Koramangala Canal",
         description="Factory drainage pipe illegally connected to the Koramangala Canal. Discharging coloured effluent.",
         wb_idx=10, citizen_idx=1, lat=12.935, lng=77.635,
         has_construction=True, has_permission=False, affected_area_level="HIGH",
         target_status="ACTION_REQUIRED", days_ago=20),
]


# ──────────────────────────────────────────────────────────────
# 4.  STATUS LIFECYCLE TRANSITIONS
# ──────────────────────────────────────────────────────────────
STATUS_CHAINS = {
    "SUBMITTED":            ["SUBMITTED"],
    "AI_REVIEWED":          ["SUBMITTED", "AI_REVIEWED"],
    "ASSIGNED":             ["SUBMITTED", "AI_REVIEWED", "ASSIGNED"],
    "UNDER_VERIFICATION":   ["SUBMITTED", "AI_REVIEWED", "ASSIGNED", "UNDER_VERIFICATION"],
    "ACTION_REQUIRED":      ["SUBMITTED", "AI_REVIEWED", "ASSIGNED", "UNDER_VERIFICATION", "ACTION_REQUIRED"],
    "ACTION_TAKEN":         ["SUBMITTED", "AI_REVIEWED", "ASSIGNED", "UNDER_VERIFICATION", "ACTION_REQUIRED", "ACTION_TAKEN"],
    "RESOLVED":             ["SUBMITTED", "AI_REVIEWED", "ASSIGNED", "UNDER_VERIFICATION", "ACTION_REQUIRED", "ACTION_TAKEN", "RESOLVED"],
    "REJECTED":             ["SUBMITTED", "AI_REVIEWED", "REJECTED"],
}

STATUS_REMARKS = {
    "SUBMITTED":            "Complaint submitted by citizen via web portal.",
    "AI_REVIEWED":          "AI Knowledge-Based reasoning completed. Forward Chaining analysis executed.",
    "ASSIGNED":             "Complaint assigned to responsible authority via CSP constraint solver.",
    "UNDER_VERIFICATION":   "Authority officer has accepted the case and initiated field verification.",
    "ACTION_REQUIRED":      "Field verification confirms encroachment indicators. Corrective action ordered.",
    "ACTION_TAKEN":         "Demolition/removal action executed by enforcement team at site.",
    "RESOLVED":             "Case resolved. Area restored and compliance verified in follow-up inspection.",
    "REJECTED":             "Complaint rejected after review. Classified as duplicate or non-actionable.",
}


# ──────────────────────────────────────────────────────────────
# 5.  MAIN SEED FUNCTION
# ──────────────────────────────────────────────────────────────
def run_seed():
    with app.app_context():
        print("\n" + "=" * 60)
        print("  WATER BODY ENCROACHMENT SYSTEM — SEED SCRIPT")
        print("=" * 60)

        # ── Clean existing data (reverse-dependency order) ──
        print("\n[1/8] Cleaning existing data...")
        ComplaintStatusHistory.query.delete()
        AuthorityAssignment.query.delete()
        ComplaintEvidence.query.delete()
        Complaint.query.delete()
        Rule.query.delete()
        Authority.query.delete()
        WaterBody.query.delete()
        User.query.delete()
        db.session.commit()
        print("      ✓ All tables cleared.")

        # ── Seed Users ──
        print("[2/8] Seeding users...")
        user_objects = []
        for u in USERS:
            user = User(name=u["name"], email=u["email"], password_hash=PW_HASH,
                        role=u["role"], phone=u["phone"])
            db.session.add(user)
            user_objects.append(user)
        db.session.flush()
        citizen_users = [u for u in user_objects if u.role == "citizen"]
        authority_users = [u for u in user_objects if u.role in ("authority", "admin")]
        print(f"      ✓ {len(user_objects)} users created ({len(citizen_users)} citizens, {len(authority_users)} officials)")

        # ── Seed Water Bodies ──
        print("[3/8] Seeding water bodies...")
        wb_objects = []
        for wb in WATER_BODIES:
            obj = WaterBody(**wb)
            db.session.add(obj)
            wb_objects.append(obj)
        db.session.flush()
        print(f"      ✓ {len(wb_objects)} water bodies created")

        # ── Seed Authorities ──
        print("[4/8] Seeding authorities...")
        auth_objects = []
        for a in AUTHORITIES:
            obj = Authority(**a)
            db.session.add(obj)
            auth_objects.append(obj)
        db.session.flush()
        active_count = sum(1 for a in auth_objects if a.status == "ACTIVE")
        inactive_count = sum(1 for a in auth_objects if a.status == "INACTIVE")
        print(f"      ✓ {len(auth_objects)} authorities created ({active_count} active, {inactive_count} inactive)")

        # ── Seed Rules ──
        print("[5/8] Seeding AI rules...")
        for r in RULES:
            obj = Rule(**r, active=True)
            db.session.add(obj)
        db.session.flush()
        print(f"      ✓ {len(RULES)} rules created")

        # ── Seed Complaints (with live AI) ──
        print("[6/8] Seeding complaints with LIVE AI reasoning...")
        complaint_objects = []
        assignment_count = 0
        history_count = 0
        ai_results_summary = {}

        for idx, c in enumerate(COMPLAINTS):
            water_body = wb_objects[c["wb_idx"]]
            citizen = citizen_users[c["citizen_idx"]]
            created_at = ts(days_ago=c["days_ago"])

            # Check boundary using actual MapService
            inside_boundary, boundary_note = MapService.check_boundary_intersection(
                c["lat"], c["lng"], water_body
            )

            complaint = Complaint(
                user_id=citizen.id,
                water_body_id=water_body.id,
                title=c["title"],

                description=c["description"],
                latitude=c["lat"],
                longitude=c["lng"],
                has_construction=c["has_construction"],
                inside_boundary=inside_boundary,
                has_permission=c["has_permission"],
                affected_area_level=c["affected_area_level"],
                status="SUBMITTED",
                created_at=created_at,
                updated_at=created_at
            )
            db.session.add(complaint)
            db.session.flush()

            # ── Run REAL Forward Chaining AI ──
            complaint_dict = {
                "has_construction": complaint.has_construction,
                "inside_boundary": complaint.inside_boundary,
                "has_permission": complaint.has_permission,
                "affected_area_level": complaint.affected_area_level,
                "water_body_type": water_body.type,
                "district": water_body.district,
                "has_evidence": False
            }
            kb = KnowledgeBase.from_complaint(complaint_dict)
            engine = ForwardChainingEngine(kb)
            ai_result = engine.run_inference()

            complaint.classification = ai_result["preliminary_result"]
            complaint.priority = ai_result["priority"]

            # ── Run REAL CSP Authority Assignment ──
            authorities_dicts = [a.to_dict() for a in auth_objects]
            workloads = (
                db.session.query(AuthorityAssignment.authority_id, db.func.count(AuthorityAssignment.id))
                .filter(AuthorityAssignment.status == "ASSIGNED")
                .group_by(AuthorityAssignment.authority_id)
                .all()
            )
            current_workloads = {aid: cnt for aid, cnt in workloads}
            csp_info = {"water_body_type": water_body.type, "district": water_body.district}
            csp = AuthorityCSP(authorities_dicts, current_workloads)
            csp_result = csp.solve(csp_info)

            complaint.ai_reasoning_trace = {
                "forward_chaining": ai_result,
                "csp_assignment": csp_result,
                "boundary_check": {
                    "inside_boundary": inside_boundary,
                    "note": boundary_note
                }
            }

            # ── Create authority assignment if CSP succeeded and status warrants ──
            target = c["target_status"]
            assign_statuses = {"ASSIGNED", "UNDER_VERIFICATION", "ACTION_REQUIRED", "ACTION_TAKEN", "RESOLVED"}
            if csp_result.get("success") and target in assign_statuses:
                auth_data = csp_result["assigned_authority"]
                assignment = AuthorityAssignment(
                    complaint_id=complaint.id,
                    authority_id=auth_data["id"],
                    assigned_by="AI_CSP_SYSTEM",
                    assignment_reason=csp_result.get("assignment_reason"),
                    status="ASSIGNED",
                    assigned_at=ts(days_ago=c["days_ago"], hours_ago=-2)
                )
                db.session.add(assignment)
                assignment_count += 1

            # ── Set final status ──
            complaint.status = target
            complaint.updated_at = ts(days_ago=max(0, c["days_ago"] - 1))

            # ── Build status history chain ──
            chain = STATUS_CHAINS.get(target, ["SUBMITTED"])
            for step_idx, status in enumerate(chain):
                history = ComplaintStatusHistory(
                    complaint_id=complaint.id,
                    old_status=chain[step_idx - 1] if step_idx > 0 else None,
                    new_status=status,
                    remarks=STATUS_REMARKS.get(status, "Status updated."),
                    changed_by=citizen.id if status == "SUBMITTED" else authority_users[0].id,
                    changed_at=ts(days_ago=c["days_ago"], hours_ago=-(step_idx * 6))
                )
                db.session.add(history)
                history_count += 1

            complaint_objects.append(complaint)

            # Track AI classification distribution
            cls_key = ai_result["preliminary_result"]
            ai_results_summary[cls_key] = ai_results_summary.get(cls_key, 0) + 1

            print(f"      [{idx+1:2d}/{len(COMPLAINTS)}] C#{complaint.id}: "
                  f"{complaint.classification[:35]:35s} | Priority: {complaint.priority:6s} | Status: {target}")

        # ── Sample evidence metadata (no actual files) ──
        print("[7/8] Seeding evidence metadata...")
        evidence_count = 0
        evidence_complaints = [c for c in complaint_objects if c.has_construction and c.status not in ("SUBMITTED", "REJECTED")]
        for comp in evidence_complaints[:10]:
            ev = ComplaintEvidence(
                complaint_id=comp.id,
                file_path=f"uploads/demo_evidence_{comp.id}.jpg",
                file_type="image/jpeg",
                original_filename=f"site_photo_{comp.id}.jpg",
                uploaded_at=comp.created_at
            )
            db.session.add(ev)
            evidence_count += 1
        db.session.flush()
        print(f"      ✓ {evidence_count} evidence records created")

        # ── Commit everything ──
        print("[8/8] Committing to PostgreSQL...")
        db.session.commit()
        print("      ✓ All data committed successfully.")

        # ──────────────────────────────────────────────────────
        #  VALIDATION
        # ──────────────────────────────────────────────────────
        print("\n" + "─" * 60)
        print("  VALIDATION")
        print("─" * 60)

        u_count = User.query.count()
        wb_count = WaterBody.query.count()
        a_count = Authority.query.count()
        r_count = Rule.query.count()
        c_count = Complaint.query.count()
        h_count = ComplaintStatusHistory.query.count()
        as_count = AuthorityAssignment.query.count()
        ev_count = ComplaintEvidence.query.count()

        checks = [
            ("Users created",           u_count > 0,  u_count),
            ("Water bodies created",    wb_count > 0, wb_count),
            ("Authorities created",     a_count > 0,  a_count),
            ("Rules created",           r_count > 0,  r_count),
            ("Complaints created",      c_count >= 20, c_count),
            ("Status history records",  h_count > 0,  h_count),
            ("Authority assignments",   as_count > 0, as_count),
            ("Evidence records",        ev_count > 0, ev_count),
            ("Inactive authority exists", Authority.query.filter_by(status="INACTIVE").count() > 0, "YES"),
            ("Forward Chaining works",  any("Requires" in c.classification or "Possible" in c.classification for c in complaint_objects if c.has_construction and c.inside_boundary), "YES"),
            ("CSP assignment works",    as_count > 0, "YES"),
        ]

        all_pass = True
        for label, passed, value in checks:
            status = "✓" if passed else "✗"
            if not passed:
                all_pass = False
            print(f"  {status} {label:35s} : {value}")

        # Status distribution
        print("\n  Status Distribution:")
        for status_val in ["SUBMITTED", "AI_REVIEWED", "ASSIGNED", "UNDER_VERIFICATION",
                           "ACTION_REQUIRED", "ACTION_TAKEN", "RESOLVED", "REJECTED"]:
            cnt = Complaint.query.filter_by(status=status_val).count()
            print(f"    {status_val:25s} : {cnt}")

        # AI classification distribution
        print("\n  AI Classification Distribution:")
        for cls_name, cnt in sorted(ai_results_summary.items()):
            print(f"    {cls_name:45s} : {cnt}")

        print("\n" + "=" * 60)
        if all_pass:
            print("  ✅  SEED COMPLETE — ALL VALIDATIONS PASSED")
        else:
            print("  ⚠️  SEED COMPLETE — SOME VALIDATIONS NEED REVIEW")
        print("=" * 60)

        print(f"""
  Summary:
    Users            : {u_count}
    Water Bodies     : {wb_count}
    Authorities      : {a_count}
    Rules            : {r_count}
    Complaints       : {c_count}
    Assignments      : {as_count}
    Status History   : {h_count}
    Evidence Records : {ev_count}

  Demo Credentials (Password for all: Password@123):
    Admin     : admin@waterbodies.gov.in
    Authority : officer.revenue@waterbodies.gov.in
    Authority : officer.municipal@waterbodies.gov.in
    Citizen   : citizen1@example.com
    Citizen   : citizen2@example.com
    Citizen   : citizen3@example.com
""")


if __name__ == "__main__":
    run_seed()
