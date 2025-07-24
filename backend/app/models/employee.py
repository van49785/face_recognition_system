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
    
    # FIXED: Lấy tiến độ training khuôn mặt với auto-complete
    def get_face_training_progress(self):
        """Trả về thông tin tiến độ training khuôn mặt và tự động complete nếu đủ pose"""
        poses_count = FaceTrainingData.get_employee_pose_count(self.employee_id)
        required_poses = 5  # Số pose tối thiểu cần thiết
        
        progress_data = {
            'poses_completed': poses_count,
            'poses_required': required_poses,
            'progress_percentage': (poses_count / required_poses) * 100 if required_poses > 0 else 0,
            'is_completed': poses_count >= required_poses
        }
        
        # AUTO-COMPLETE: Tự động đánh dấu hoàn thành nếu đủ pose và chưa được đánh dấu
        if poses_count >= required_poses and not self.face_training_completed:
            self.complete_face_training()
            print(f"✅ Auto-completed face training for employee {self.employee_id}")
        
        return progress_data
    
    # FIXED: Đánh dấu hoàn thành training khuôn mặt
    def complete_face_training(self):
        """Cập nhật trạng thái training khuôn mặt khi đủ số pose"""
        self.face_training_completed = True
        self.face_training_date = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
        self.total_poses_trained = FaceTrainingData.get_employee_pose_count(self.employee_id)
        
        # Commit changes to database
        try:
            db.session.commit()
            print(f"✅ Face training completed for {self.employee_id} with {self.total_poses_trained} poses")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error completing face training for {self.employee_id}: {e}")
            raise e
    
    # NEW: Method để check và update training status
    def check_and_update_training_status(self):
        """Kiểm tra và cập nhật trạng thái training nếu cần thiết"""
        poses_count = FaceTrainingData.get_employee_pose_count(self.employee_id)
        
        # Cập nhật total_poses_trained nếu không khớp
        if self.total_poses_trained != poses_count:
            self.total_poses_trained = poses_count
        
        # Đánh dấu complete nếu đủ pose nhưng chưa được đánh dấu
        if poses_count >= 5 and not self.face_training_completed:
            self.face_training_completed = True
            self.face_training_date = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
            
        # Bỏ đánh dấu complete nếu không đủ pose
        elif poses_count < 5 and self.face_training_completed:
            self.face_training_completed = False
            self.face_training_date = None
            
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating training status for {self.employee_id}: {e}")
            return False
    
    # Kiểm tra đủ dữ liệu training
    def has_sufficient_training_data(self):
        """Kiểm tra xem nhân viên có đủ ít nhất 3 pose để nhận diện"""
        return FaceTrainingData.get_employee_pose_count(self.employee_id) >= 3
    
    # NEW: Class method để fix tất cả employees có vấn đề về training status
    @classmethod
    def fix_all_training_status(cls):
        """Fix training status cho tất cả nhân viên có vấn đề"""
        employees = cls.query.all()
        fixed_count = 0
        
        for emp in employees:
            poses_count = FaceTrainingData.get_employee_pose_count(emp.employee_id)
            needs_update = False
            
            # Case 1: Đủ pose nhưng chưa được đánh dấu complete
            if poses_count >= 5 and not emp.face_training_completed:
                emp.face_training_completed = True
                emp.face_training_date = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
                needs_update = True
                print(f"🔧 Fixed: {emp.employee_id} had {poses_count} poses but not marked as completed")
            
            # Case 2: Không đủ pose nhưng được đánh dấu complete
            elif poses_count < 5 and emp.face_training_completed:
                emp.face_training_completed = False
                emp.face_training_date = None
                needs_update = True
                print(f"🔧 Fixed: {emp.employee_id} marked complete but only has {poses_count} poses")
            
            # Case 3: total_poses_trained không khớp với thực tế
            if emp.total_poses_trained != poses_count:
                emp.total_poses_trained = poses_count
                needs_update = True
                print(f"🔧 Fixed: {emp.employee_id} pose count updated from {emp.total_poses_trained} to {poses_count}")
            
            if needs_update:
                fixed_count += 1
        
        try:
            db.session.commit()
            print(f"✅ Fixed training status for {fixed_count} employees")
            return fixed_count
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error fixing training status: {e}")
            return 0
    
    # Chuỗi đại diện cho đối tượng
    def __repr__(self):
        """Trả về chuỗi mô tả nhân viên"""
        return f'<Employee {self.employee_id}: {self.full_name} (Training: {self.face_training_completed})>'