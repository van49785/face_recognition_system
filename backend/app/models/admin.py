from app.db import db
from datetime import datetime, timezone, timedelta
from app.utils.security import hash_password, check_password_hash

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    role = db.Column(db.String(32), default='admin', nullable=False)
    last_login = db.Column(db.DateTime, index=True)  # Thêm index để tối ưu truy vấn
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    sessions = db.relationship('Session', backref='admin', lazy=True)
    logs = db.relationship('AuditLog', backref='admin', lazy=True)
    
    def set_password(self, password):
        """Hash và lưu password"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """Kiểm tra password và cập nhật failed_attempts"""
        if not self.check_password_hash(self.password_hash, password):
            self.failed_attempts += 1
            if self.failed_attempts >= 5:
                self.lock_account()
            return False
        self.failed_attempts = 0  # Reset sau khi đăng nhập thành công
        self.last_login = datetime.now(timezone.utc)
        return True
    
    def check_password_hash(self, password_hash, password):
        """Tách riêng để có thể tái sử dụng"""
        return check_password_hash(password_hash, password)
    
    def is_locked(self):
        """Kiểm tra tài khoản có bị khóa hoặc không hoạt động"""
        if not self.is_active:
            return True
        if self.locked_until:
            return datetime.now(timezone.utc) < self.locked_until
        return False
    
    def lock_account(self, duration_minutes=30):
        """Khóa tài khoản trong thời gian nhất định"""
        self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        self.failed_attempts = 0
        db.session.commit()  # Đảm bảo thay đổi được lưu
    
    def unlock_account(self):
        """Mở khóa tài khoản"""
        self.locked_until = None
        self.failed_attempts = 0
        db.session.commit()  # Đảm bảo thay đổi được lưu
    
    def __repr__(self):
        return f'<Admin {self.username}>'