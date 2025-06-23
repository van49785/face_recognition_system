from app.db import db
from datetime import datetime, timezone, timedelta
import secrets
import hashlib

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False, index=True)
    jwt_token_hash = db.Column(db.String(64), nullable=False)
    issued_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_valid = db.Column(db.Boolean, default=True, nullable=False)
    last_activity = db.Column(db.DateTime, nullable=False)
    ip_address = db.Column(db.String(15))  # IPv4, tối đa 15 ký tự
    user_agent = db.Column(db.String(500))
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.session_id:
            self.session_id = secrets.token_urlsafe(32)
        if not self.issued_at:
            self.issued_at = datetime.now(timezone.utc)
        if not self.expires_at:
            self.expires_at = self.issued_at + timedelta(hours=2)
        if not self.last_activity:
            self.last_activity = self.issued_at
    
    @staticmethod
    def validate_ip_address(ip_address):
        """Validate IPv4 address"""
        if not ip_address:
            return True
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        import re
        if not re.match(pattern, ip_address):
            raise ValueError("Invalid IPv4 address format")
        return True
    
    @staticmethod
    def hash_token(token):
        """Hash JWT token bằng SHA256"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @classmethod
    def create_session(cls, admin_id, jwt_token, ip_address=None, user_agent=None):
        """Factory method để tạo session"""
        cls.validate_ip_address(ip_address)
        return cls(
            admin_id=admin_id,
            jwt_token_hash=cls.hash_token(jwt_token),
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def is_expired(self):
        """Kiểm tra session có hết hạn không"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def is_active(self):
        """Kiểm tra session có hoạt động không"""
        return self.is_valid and not self.is_expired()
    
    def invalidate(self):
        """Vô hiệu hóa session"""
        self.is_valid = False
        db.session.commit()  # Đảm bảo lưu thay đổi
    
    def update_activity(self, extend_duration=False):
        """Cập nhật thời gian hoạt động cuối, có thể gia hạn session"""
        self.last_activity = datetime.now(timezone.utc)
        if extend_duration and self.is_valid:
            self.expires_at = self.last_activity + timedelta(hours=2)
        db.session.commit()  # Đảm bảo lưu thay đổi
    
    @classmethod
    def cleanup_expired(cls):
        """Cleanup các session hết hạn"""
        expired_sessions = cls.query.filter(
            cls.expires_at < datetime.now(timezone.utc)
        ).all()
        count = len(expired_sessions)
        for session in expired_sessions:
            db.session.delete(session)
        db.session.commit()  # Đảm bảo xóa khỏi database
        return count
    
    def __repr__(self):
        return f'<Session {self.session_id}: Admin {self.admin_id}>'