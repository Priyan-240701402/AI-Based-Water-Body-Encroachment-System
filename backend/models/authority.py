from datetime import datetime, timezone
from backend.database import db

class Authority(db.Model):
    __tablename__ = "authorities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=False, index=True) # 'MUNICIPAL', 'REVENUE', 'WATER_RESOURCES', 'ENVIRONMENTAL'
    jurisdiction = db.Column(db.String(100), nullable=False, index=True) # District or zone
    contact = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(30), default="ACTIVE", index=True) # 'ACTIVE', 'INACTIVE', 'OVERLOADED'
    max_active_cases = db.Column(db.Integer, default=20)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Relationships
    assignments = db.relationship("AuthorityAssignment", backref="authority", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "jurisdiction": self.jurisdiction,
            "contact": self.contact,
            "email": self.email,
            "status": self.status,
            "max_active_cases": self.max_active_cases,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
