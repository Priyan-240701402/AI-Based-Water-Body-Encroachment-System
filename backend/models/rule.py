from datetime import datetime, timezone
from backend.database import db

class Rule(db.Model):
    __tablename__ = "rules"

    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    conditions = db.Column(db.JSON, nullable=False) # Dictionary / JSON structure of antecedents
    conclusion = db.Column(db.String(120), nullable=False) # Consequent proposition
    priority = db.Column(db.Integer, default=1)
    active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "rule_name": self.rule_name,
            "description": self.description,
            "conditions": self.conditions,
            "conclusion": self.conclusion,
            "priority": self.priority,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
