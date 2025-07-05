# Import các thư viện cần thiết
from app import db  # SQLAlchemy database instance
from datetime import datetime, timezone, date  # Xử lý thời gian
import uuid  # Tạo ID duy nhất
import pytz  # Xử lý múi giờ

# Model lưu trữ bản ghi chấm công
class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    employee_id = db.Column(db.String(8), db.ForeignKey('employees.employee_id'), 
                           nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False)  # check-in, check-out
    location = db.Column(db.String(100))
    device_info = db.Column(db.String(255))
    # Đồng bộ timezone với Employee model - sử dụng Asia/Ho_Chi_Minh
    created_at = db.Column(db.DateTime, 
                          default=lambda: datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None), 
                          nullable=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.attendance_id:
            self.attendance_id = str(uuid.uuid4())
        if not self.timestamp:
            # Sử dụng timezone Việt Nam thay vì UTC
            self.timestamp = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
    
    @staticmethod
    def validate_status(status):
        """Validate attendance status"""
        valid_statuses = ['check-in', 'check-out']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        return True
    
    @staticmethod
    def validate_location(location):
        """Validate location (nếu có)"""
        if location and len(location) > 100:
            raise ValueError("Location must not exceed 100 characters")
        return True
    
    @staticmethod
    def validate_device_info(device_info):
        """Validate device info (nếu có)"""
        if device_info and len(device_info) > 255:
            raise ValueError("Device info must not exceed 255 characters")
        return True
    
    @classmethod
    def create_attendance(cls, employee_id, status, location=None, device_info=None):
        """Factory method để tạo attendance record"""
        cls.validate_status(status)
        cls.validate_location(location)
        cls.validate_device_info(device_info)
        
        return cls(
            employee_id=employee_id,
            status=status,
            location=location,
            device_info=device_info
        )
    
    @classmethod
    def get_today_records(cls, employee_id=None):
        """Lấy records hôm nay - đồng bộ với timezone Việt Nam"""
        today = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).date()
        query = cls.query.filter(
            db.func.date(cls.timestamp) == today
        )
        if employee_id:
            query = query.filter(cls.employee_id == employee_id)
        return query.order_by(cls.timestamp.desc()).all()
    
    def __repr__(self):
        return f'<Attendance {self.employee_id}: {self.status} at {self.timestamp}>'