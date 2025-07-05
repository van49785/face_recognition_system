# Import các thư viện cần thiết
from app.db import db  # SQLAlchemy database instance
from datetime import datetime  # Xử lý thời gian
import uuid  # Tạo ID duy nhất cho training data
import pytz  # Xử lý múi giờ

# Model lưu trữ dữ liệu training khuôn mặt cho từng nhân viên
class FaceTrainingData(db.Model):
    __tablename__ = 'face_training_data'  # Tên bảng trong database
    
    # Các cột trong bảng
    id = db.Column(db.Integer, primary_key=True)  # ID chính, tự động tăng
    training_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # ID duy nhất cho mỗi bản ghi training
    employee_id = db.Column(db.String(8), db.ForeignKey('employees.employee_id'), 
                           nullable=False, index=True)  # Khóa ngoại liên kết với bảng employees
    pose_type = db.Column(db.String(20), nullable=False)  # Loại pose (front, left, right, up, down)
    face_encoding = db.Column(db.LargeBinary, nullable=False)  # Mã hóa khuôn mặt dạng binary
    image_quality_score = db.Column(db.Float)  # Điểm chất lượng ảnh (tùy chọn)
    created_at = db.Column(db.DateTime, 
                          default=lambda: datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None), 
                          nullable=False)  # Thời gian tạo bản ghi, mặc định là giờ Việt Nam

    # Khởi tạo bản ghi mới
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Tự động tạo training_id nếu chưa có
        if not self.training_id:
            self.training_id = str(uuid.uuid4())
    
    # Kiểm tra tính hợp lệ của pose_type
    @staticmethod
    def validate_pose_type(pose_type):
        """Kiểm tra pose_type có thuộc danh sách hợp lệ không"""
        valid_poses = ['front', 'left', 'right', 'up', 'down']  # Danh sách pose được phép
        if pose_type not in valid_poses:
            raise ValueError(f"Invalid pose type: {pose_type}. Must be one of {valid_poses}")
        return True
    
    # Factory method để tạo bản ghi FaceTrainingData
    @classmethod
    def create_training_data(cls, employee_id, pose_type, face_encoding, image_quality_score=None):
        """Tạo bản ghi training mới với thông tin nhân viên, pose, và encoding"""
        cls.validate_pose_type(pose_type)  # Xác thực pose_type
        return cls(
            employee_id=employee_id,
            pose_type=pose_type,
            face_encoding=face_encoding,
            image_quality_score=image_quality_score
        )
    
    # Lấy tất cả encodings của một nhân viên
    @classmethod
    def get_employee_encodings(cls, employee_id):
        """Trả về danh sách tất cả bản ghi training của một nhân viên"""
        return cls.query.filter_by(employee_id=employee_id).all()
    
    # Đếm số lượng pose đã train cho một nhân viên
    @classmethod
    def get_employee_pose_count(cls, employee_id):
        """Trả về số lượng pose đã được lưu cho một nhân viên"""
        return cls.query.filter_by(employee_id=employee_id).count()