from datetime import datetime, timezone
from backend.database import db

class AuthorityAssignment(db.Model):
    __tablename__ = "authority_assignments"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    authority_id = db.Column(db.Integer, db.ForeignKey("authorities.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    assigned_by = db.Column(db.String(50), default="AI_CSP_SYSTEM") # 'AI_CSP_SYSTEM' or 'ADMIN'
    assignment_reason = db.Column(db.Text, nullable=True) # Reason trace explaining CSP constraints satisfied
    status = db.Column(db.String(30), default="ASSIGNED") # 'ASSIGNED', 'ACCEPTED', 'TRANSFERRED'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "authority_id": self.authority_id,
            "authority_name": self.authority.name if self.authority else None,
            "department": self.authority.department if self.authority else None,
            "jurisdiction": self.authority.jurisdiction if self.authority else None,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "assigned_by": self.assigned_by,
            "assignment_reason": self.assignment_reason,
            "status": self.status
        }
