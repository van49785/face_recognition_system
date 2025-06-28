from app.db import db
from datetime import datetime, timezone, timedelta
import secrets
import hashlib
import re
import pytz

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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Đồng bộ timezone với Employee và Attendance - sử dụng Asia/Ho_Chi_Minh
        now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
        if not self.session_id:
            self.session_id = secrets.token_urlsafe(32)
        if not self.issued_at:
            self.issued_at = now
        if not self.expires_at:
            self.expires_at = self.issued_at + timedelta(hours=2)
        if not self.last_activity:
            self.last_activity = self.issued_at

    
    @staticmethod
    def hash_token(token):
        """Hash JWT token bằng SHA256"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @classmethod
    def create_session(
        cls,
        admin_id: int,
        jwt_token: str,
    ) -> "Session":
        
        session = cls(
            admin_id=admin_id,
            jwt_token_hash=cls.hash_token(jwt_token),
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    @classmethod
    def invalidate_token_hash(cls, jwt_token: str) -> None:
        """Vô hiệu hoá (đặt is_valid=False) tất cả phiên trùng token."""
        hashed = cls.hash_token(jwt_token)
        sess = cls.query.filter_by(jwt_token_hash=hashed, is_valid=True).first()
        if sess:
            sess.is_valid = False
            db.session.commit()

    
    def is_expired(self):
        """Kiểm tra session có hết hạn không - đồng bộ timezone"""
        now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
        return now > self.expires_at
    
    def is_active(self):
        """Kiểm tra session có hoạt động không"""
        return self.is_valid and not self.is_expired()
    
    def invalidate(self):
        """Vô hiệu hóa session"""
        self.is_valid = False
        db.session.commit()
    
    def update_activity(self, extend_duration=False):
        """Cập nhật thời gian hoạt động cuối, có thể gia hạn session"""
        now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
        self.last_activity = now
        if extend_duration and self.is_valid:
            self.expires_at = self.last_activity + timedelta(hours=2)
        db.session.commit()
    
    @classmethod
    def cleanup_expired(cls):
        """Cleanup các session hết hạn"""
        now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
        expired_sessions = cls.query.filter(cls.expires_at < now).all()
        count = len(expired_sessions)
        for session in expired_sessions:
            db.session.delete(session)
        db.session.commit()
        return count
    
    def __repr__(self):
        return f'<Session {self.session_id}: Admin {self.admin_id}>'