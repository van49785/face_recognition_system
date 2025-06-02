from .. import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(db.String(12), unique=True, nullable=False, index=True)  # Mã định danh
    employee_id = db.Column(db.String(8), db.ForeignKey('employees.employee_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(10), nullable=False)  # "check-in" hoặc "check-out"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Có thể bổ sung updated_at nếu cần

    # Relationship tới Employee được định nghĩa ở Employee.attendance_records
