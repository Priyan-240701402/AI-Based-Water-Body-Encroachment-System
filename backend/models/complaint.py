from datetime import datetime, timezone
from backend.database import db

class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    water_body_id = db.Column(db.Integer, db.ForeignKey("water_bodies.id", ondelete="SET NULL"), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    classification = db.Column(db.String(80), default="Pending Preliminary Analysis")
    priority = db.Column(db.String(20), default="MEDIUM", index=True) # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    status = db.Column(db.String(40), default="SUBMITTED", nullable=False, index=True)
    # Status lifecycle: SUBMITTED -> AI_REVIEWED -> ASSIGNED -> UNDER_VERIFICATION -> ACTION_REQUIRED -> ACTION_TAKEN -> RESOLVED / REJECTED

    # AI Propositional Logic Fact Inputs
    has_construction = db.Column(db.Boolean, default=False)
    inside_boundary = db.Column(db.Boolean, default=False)
    has_permission = db.Column(db.Boolean, default=False)
    affected_area_level = db.Column(db.String(20), default="MEDIUM") # 'LOW', 'MEDIUM', 'HIGH'
    ai_reasoning_trace = db.Column(db.JSON, nullable=True) # Holds forward chaining trace & CSP assignment reason

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Relationships
    evidence = db.relationship("ComplaintEvidence", backref="complaint", lazy=True, cascade="all, delete-orphan")
    assignments = db.relationship("AuthorityAssignment", backref="complaint", lazy=True, cascade="all, delete-orphan")
    status_history = db.relationship("ComplaintStatusHistory", backref="complaint", lazy=True, cascade="all, delete-orphan", order_by="ComplaintStatusHistory.changed_at.desc()")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "citizen_name": self.citizen.name if self.citizen else None,
            "water_body_id": self.water_body_id,
            "water_body_name": self.water_body.name if self.water_body else None,
            "title": self.title,
            "description": self.description,
            "latitude": float(self.latitude) if self.latitude is not None else None,
            "longitude": float(self.longitude) if self.longitude is not None else None,
            "classification": self.classification,
            "priority": self.priority,
            "status": self.status,
            "has_construction": self.has_construction,
            "inside_boundary": self.inside_boundary,
            "has_permission": self.has_permission,
            "affected_area_level": self.affected_area_level,
            "ai_reasoning_trace": self.ai_reasoning_trace,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "evidence_count": len(self.evidence) if self.evidence else 0,
            "current_assigned_authority": (
                self.assignments[0].authority.name if self.assignments and self.assignments[0].authority else None
            )
        }
