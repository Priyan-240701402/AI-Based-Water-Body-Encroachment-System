from datetime import datetime, timezone
from backend.database import db

class ComplaintEvidence(db.Model):
    __tablename__ = "complaint_evidence"

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = db.Column(db.String(300), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    original_filename = db.Column(db.String(255), nullable=True)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "complaint_id": self.complaint_id,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "original_filename": self.original_filename,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
