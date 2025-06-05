from backend import db
from datetime import datetime, timezone

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(32), default='admin')
    last_login = db.Column(db.DateTime)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Quan hệ: 1 admin có thể có nhiều session, log
    sessions = db.relationship('Session', backref='admin', lazy=True)
    logs = db.relationship('AuditLog', backref='admin', lazy=True)
