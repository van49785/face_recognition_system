
from backend import db
from datetime import datetime, timezone

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(8), unique=True, nullable=False, index=True)  # Mã NV: 8 ký tự, dùng cho mã định danh
    full_name = db.Column(db.String(128), nullable=False)
    department = db.Column(db.String(64))
    position = db.Column(db.String(64))
    face_encoding = db.Column(db.LargeBinary, nullable=True)  # Dữ liệu mã hóa khuôn mặt
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    status = db.Column(db.Boolean, default=True)  # Hoạt động hoặc không
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Quan hệ: Một nhân viên có nhiều bản ghi chấm công
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)
