# Import các thư viện cần thiết
from app import db  
from datetime import datetime, timezone, date  
import re 
from app.models.attendance import Attendance  
from app.models.face_training_data import FaceTrainingData  
import pytz 

# Model lưu trữ thông tin nhân viên
class Employee(db.Model):
    __tablename__ = 'employees'  # Tên bảng trong database
    
    # Các cột trong bảng
    id = db.Column(db.Integer, primary_key=True) 
    employee_id = db.Column(db.String(8), unique=True, nullable=False, index=True) 
    full_name = db.Column(db.String(128), nullable=False, index=True) 
    department = db.Column(db.String(64), index=True)  
    position = db.Column(db.String(64))  
    face_encoding = db.Column(db.LargeBinary, nullable=True)  
    face_training_completed = db.Column(db.Boolean, default=False, nullable=False) 
    face_training_date = db.Column(db.DateTime, nullable=True)  
    total_poses_trained = db.Column(db.Integer, default=0)  # Số pose đã train
    phone = db.Column(db.String(20))  
    email = db.Column(db.String(120), index=True)  
    status = db.Column(db.Boolean, default=True, nullable=False)  # Trạng thái nhân viên (active/inactive)
    created_at = db.Column(db.DateTime, 
                          default=lambda: datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None), 
                          nullable=False)  
    updated_at = db.Column(db.DateTime, 
                          default=lambda: datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None),
                          onupdate=lambda: datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None))  # Thời gian cập nhật

    # Quan hệ với các bảng khác
    attendance_records = db.relationship('Attendance', backref='employee', lazy=True)  # Liên kết với bảng Attendance
    face_training_data = db.relationship('FaceTrainingData', backref='employee', lazy=True)  # Liên kết với bảng FaceTrainingData
    
    # Kiểm tra định dạng email
    @staticmethod
    def validate_email(email):
        """Validate định dạng và độ dài email"""
        if not email:
            return True
        if len(email) > 120:
            raise ValueError("Email must not exceed 120 characters")
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        return True
    
    # Kiểm tra định dạng số điện thoại
    @staticmethod
    def validate_phone(phone):
        """Validate định dạng và độ dài số điện thoại (theo chuẩn Việt Nam)"""
        if not phone:
            return True
        if len(phone) > 20:
            raise ValueError("Phone number must not exceed 20 characters")
        pattern = r'^(\+84|0)[0-9]{9,10}$'
        if not re.match(pattern, phone):
            raise ValueError("Invalid phone number format (must match Vietnam format)")
        return True
    
    # Lấy bản ghi chấm công mới nhất
    def get_latest_attendance(self):
        """Trả về bản ghi chấm công mới nhất của nhân viên"""
        return self.attendance_records.order_by(Attendance.timestamp.desc()).first()
    
    # Kiểm tra nhân viên đã check-in hôm nay chưa
    def is_checked_in_today(self):
        """Kiểm tra xem nhân viên có bản ghi check-in trong ngày hiện tại không"""
        today = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).date()
        latest = self.get_latest_attendance()
        if latest and latest.timestamp.date() == today:
            return latest.status == 'check-in'
        return False
    
    # Lấy tất cả bản ghi chấm công trong ngày
    def get_today_attendance_records(self):
        """Trả về tất cả bản ghi chấm công của nhân viên trong ngày hiện tại"""
        return Attendance.get_today_records(employee_id=self.employee_id)
    
    # Lấy tất cả encodings khuôn mặt
    def get_face_encodings(self):
        """Trả về danh sách encodings khuôn mặt từ bảng FaceTrainingData"""
        return FaceTrainingData.get_employee_encodings(self.employee_id)
    
    # Lấy tiến độ training khuôn mặt
    def get_face_training_progress(self):
        """Trả về thông tin tiến độ training khuôn mặt (số pose, phần trăm hoàn thành)"""
        poses_count = FaceTrainingData.get_employee_pose_count(self.employee_id)
        required_poses = 5  # Số pose tối thiểu cần thiết
        return {
            'poses_completed': poses_count,
            'poses_required': required_poses,
            'progress_percentage': (poses_count / required_poses) * 100 if required_poses > 0 else 0,
            'is_completed': poses_count >= required_poses
        }
    
    # Đánh dấu hoàn thành training khuôn mặt
    def complete_face_training(self):
        """Cập nhật trạng thái training khuôn mặt khi đủ số pose"""
        self.face_training_completed = True
        self.face_training_date = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
        self.total_poses_trained = FaceTrainingData.get_employee_pose_count(self.employee_id)
        self.face_encoding = None  # Xóa face_encoding cũ để đảm bảo tương thích
    
    # Kiểm tra đủ dữ liệu training
    def has_sufficient_training_data(self):
        """Kiểm tra xem nhân viên có đủ ít nhất 3 pose để nhận diện"""
        return FaceTrainingData.get_employee_pose_count(self.employee_id) >= 3
    
    # Chuỗi đại diện cho đối tượng
    def __repr__(self):
        """Trả về chuỗi mô tả nhân viên"""
        return f'<Employee {self.employee_id}: {self.full_name}>'