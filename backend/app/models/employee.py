from app.db import db
from datetime import datetime, timezone, date
import re
from app.models.attendance import Attendance
import pytz

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(8), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(128), nullable=False, index=True)
    department = db.Column(db.String(64), index=True)
    position = db.Column(db.String(64))
    face_encoding = db.Column(db.LargeBinary)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), index=True)
    status = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, 
                          default=lambda: datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None), 
                          nullable=False)
    updated_at = db.Column(db.DateTime, 
                          default=lambda: datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None),
                          onupdate=lambda: datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None))

    # Relationships
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)
    
    @staticmethod  
    def validate_email(email):
        """Validate email format và độ dài"""
        if not email:
            return True
        if len(email) > 120:
            raise ValueError("Email must not exceed 120 characters")
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        return True
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number (Vietnam format) và độ dài"""
        if not phone:
            return True
        if len(phone) > 20:
            raise ValueError("Phone number must not exceed 20 characters")
        pattern = r'^(\+84|0)[0-9]{9,10}$'
        if not re.match(pattern, phone):
            raise ValueError("Invalid phone number format (must match Vietnam format)")
        return True
    
    def get_latest_attendance(self):
        """Lấy record chấm công mới nhất"""
        return self.attendance_records.order_by(Attendance.timestamp.desc()).first()
    
    def is_checked_in_today(self):
        """Kiểm tra đã check-in hôm nay chưa - đồng bộ với timezone Việt Nam"""
        today = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).date()
        latest = self.get_latest_attendance()
        if latest and latest.timestamp.date() == today:
            return latest.status == 'check-in'
        return False
    
    def get_today_attendance_records(self):
        """Lấy tất cả records chấm công hôm nay của employee này"""
        return Attendance.get_today_records(employee_id=self.employee_id)
    
    def __repr__(self):
        return f'<Employee {self.employee_id}: {self.full_name}>'