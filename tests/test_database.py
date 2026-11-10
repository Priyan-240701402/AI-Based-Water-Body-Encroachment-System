
"""
Database Integrity, Relational Constraints & Transaction Tests.
Validates PostgreSQL schema models, foreign keys, cascades, and rollbacks.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from backend.app import create_app
from backend.database import db
from backend.models.user import User
from backend.models.complaint import Complaint
from backend.models.water_body import WaterBody
from backend.models.evidence import ComplaintEvidence
from backend.models.assignment import AuthorityAssignment
from backend.models.history import ComplaintStatusHistory

@pytest.fixture
def app_ctx():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app

def test_database_user_unique_constraint(app_ctx):
    """Verifies UNIQUE constraint on User email."""
    u1 = User(name="User A", email="unique@example.com", password_hash="hash1", role="citizen")
    db.session.add(u1)
    db.session.commit()

    u2 = User(name="User B", email="unique@example.com", password_hash="hash2", role="citizen")
    db.session.add(u2)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

def test_database_complaint_foreign_key_and_cascade(app_ctx):
    """Verifies foreign key relationships and cascade deletion."""
    user = User(name="Cascade User", email="cascade@example.com", password_hash="hash", role="citizen")
    db.session.add(user)
    db.session.commit()

    wb = WaterBody(name="Test Lake", type="LAKE", district="Central Zone")
    db.session.add(wb)
    db.session.commit()

    complaint = Complaint(
        user_id=user.id,
        water_body_id=wb.id,
        title="Test Cascade",
        description="Testing foreign keys",
        latitude=12.9800,
        longitude=77.6000
    )
    db.session.add(complaint)
    db.session.commit()

    # Add evidence and history
    evidence = ComplaintEvidence(complaint_id=complaint.id, file_path="uploads/test.jpg", file_type="image/jpeg")
    
    history = ComplaintStatusHistory(complaint_id=complaint.id, new_status="SUBMITTED", remarks="Created")
    db.session.add_all([evidence, history])
    db.session.commit()

    complaint_id = complaint.id

    # Verify relationships query
    assert len(complaint.evidence) == 1
    assert len(complaint.status_history) == 1

    # Delete complaint: Cascade must remove evidence and history records
    db.session.delete(complaint)
    db.session.commit()

    assert ComplaintEvidence.query.filter_by(complaint_id=complaint_id).count() == 0
    assert ComplaintStatusHistory.query.filter_by(complaint_id=complaint_id).count() == 0

def test_database_transaction_rollback(app_ctx):
    """Verifies that failed transaction leaves no partial/orphan records."""
    initial_user_count = User.query.count()

    try:
        # Add valid user
        u = User(name="Valid", email="rollback_test@example.com", password_hash="hash", role="citizen")
        db.session.add(u)
        db.session.flush()

        # Add invalid user that violates unique or not null
        invalid_u = User(name=None, email=None, password_hash=None) # Violates NOT NULL
        db.session.add(invalid_u)
        db.session.commit()
    except Exception:
        db.session.rollback()

    assert User.query.count() == initial_user_count
    assert User.query.filter_by(email="rollback_test@example.com").first() is None
