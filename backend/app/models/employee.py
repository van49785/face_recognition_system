from app import db
from datetime import datetime, timezone, date
import re
from app.models.attendance import Attendance

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(8), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(128), nullable=False, index=True)
    department = db.Column(db.String(64), index=True)
    position = db.Column(db.String(64))
    face_encoding = db.Column(db.LargeBinary)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), index=True)  # Thêm index để tối ưu tìm kiếm
    status = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)
    
    @staticmethod
    def validate_employee_id(employee_id):
        """Validate định dạng employee_id (8 ký tự alphanumeric)"""
        if not employee_id or len(employee_id) != 8:
            raise ValueError("Employee ID must be exactly 8 characters")
        if not re.match(r'^[A-Z0-9]{8}$', employee_id.upper()):
            raise ValueError("Employee ID must be alphanumeric")
        return True
    
    @staticmethod  
    def validate_email(email):
        """Validate email format và độ dài"""
        if not email:
            return True  # Email không bắt buộc
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
            return True  # Phone không bắt buộc
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
        """Kiểm tra đã check-in hôm nay chưa, xử lý múi giờ"""
        today = datetime.now(timezone.utc).date()
        latest = self.get_latest_attendance()
        if latest and latest.timestamp.replace(tzinfo=timezone.utc).date() == today:
            return latest.status == 'check-in'
        return False
    
    def __repr__(self):
        return f'<Employee {self.employee_id}: {self.full_name}>'