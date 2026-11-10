from datetime import datetime, timezone
from backend.database import db

class WaterBody(db.Model):
    __tablename__ = "water_bodies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50), nullable=False, index=True) # 'LAKE', 'POND', 'CANAL', 'RIVER', 'WETLAND'
    district = db.Column(db.String(100), nullable=False, index=True)
    boundary_data = db.Column(db.Text, nullable=True) # GeoJSON string or boundary coordinates
    status = db.Column(db.String(50), default="PROTECTED") # 'PROTECTED', 'UNDER_THREAT', 'CRITICAL'
    center_latitude = db.Column(db.Numeric(10, 7), nullable=True)
    center_longitude = db.Column(db.Numeric(10, 7), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Relationships
    complaints = db.relationship("Complaint", backref="water_body", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "district": self.district,
            "boundary_data": self.boundary_data,
            "status": self.status,
            "center_latitude": float(self.center_latitude) if self.center_latitude is not None else None,
            "center_longitude": float(self.center_longitude) if self.center_longitude is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
