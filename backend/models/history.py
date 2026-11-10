from datetime import datetime, timezone
from backend.database import db

class ComplaintStatusHistory(db.Model):
    __tablename__ = "complaint_status_history"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status = db.Column(db.String(40), nullable=True)
    new_status = db.Column(db.String(40), nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    changed_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship to user
    author = db.relationship("User", foreign_keys=[changed_by])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "remarks": self.remarks,
            "changed_by": self.changed_by,
            "changed_by_name": self.author.name if self.author else "System / AI",
            "changed_at": self.changed_at.isoformat() if self.changed_at else None
        }
