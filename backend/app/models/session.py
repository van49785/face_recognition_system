from app import db
from datetime import datetime, timezone

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    jwt_token = db.Column(db.String(512), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    is_valid = db.Column(db.Boolean, default=True)
