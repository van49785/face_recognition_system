# backend/app/services/attendance_service.py 

from datetime import datetime, timedelta, time
import pytz
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import base64
import os
from app import db
from app.services.facial_service import FacialRecognitionService
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.face_training_data import FaceTrainingData
from app.models.settings import Settings
from app.utils.helpers import get_vn_datetime, format_datetime_vn, format_time_vn, get_upload_path

def recognize_face_logic(image_file, base64_image, location, device_info, session_id: str):
    """Logic nhận diện khuôn mặt và ghi nhận chấm công với settings validation"""
    # Kiểm tra đầu vào
    if not image_file and not base64_image:
        return None, {"error": "No image provided"}, 400

    # Lấy settings hiện tại
    settings = Settings.get_current_settings()

    # Đọc & chuẩn hóa ảnh
    try:
        if base64_image:
            if base64_image.startswith('data:'):
                base64_image = base64_image.split(',', 1)[1]
            raw_bytes = base64.b64decode(base64_image)
        else:
            raw_bytes = image_file.read()

        nparr = np.frombuffer(raw_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return None, {"error": "Cannot decode image"}, 400
    except Exception:
        return None, {"error": "Invalid image input"}, 400

    # Nhận diện khuôn mặt
    success, message, employee = FacialRecognitionService.recognize_face_with_liveness(image, session_id)
    if not success:
        return None, {"error": message}, 400
    if not employee:
        return None, {"error": "Employee not found from face recognition"}, 404

    employee_id = employee.employee_id
    full_name = employee.full_name
    department = employee.department

    # Lấy thời gian hiện tại
    current_time = get_vn_datetime()
    current_date = current_time.date()
    current_hour = current_time.time()

    # Lấy log chấm công hôm nay
    records_today = Attendance.get_today_records(employee_id=employee_id)
    statuses = [r.status for r in records_today]

    # Kiểm tra policy constraints nếu enabled
    if settings.enable_policies:
        checkin_count = statuses.count("check-in")
        checkout_count = statuses.count("check-out")
        
        if checkin_count >= settings.max_checkins_per_day and "check-in" not in statuses:
            return None, {
                "error": f"Maximum check-ins per day ({settings.max_checkins_per_day}) exceeded"
            }, 400
            
        if checkout_count >= settings.max_checkouts_per_day and "check-out" not in statuses:
            return None, {
                "error": f"Maximum check-outs per day ({settings.max_checkouts_per_day}) exceeded"
            }, 400

    # Xác định trạng thái
    if "check-in" not in statuses:
        status = "check-in"
        
        # Áp dụng time validation nếu enabled
        if settings.enable_time_management and settings.enable_time_validation:
            if current_hour < settings.checkin_start_window:
                return None, {
                    "error": f"Check-in not allowed before {settings.checkin_start_window.strftime('%H:%M')}",
                    "next_valid_time": format_time_vn(datetime.combine(current_date, settings.checkin_start_window))
                }, 400
            elif current_hour > settings.checkin_end_window:
                return None, {
                    "error": f"Check-in not allowed after {settings.checkin_end_window.strftime('%H:%M')}"
                }, 400
            elif settings.lunch_start <= current_hour <= settings.lunch_end:
                attendance_type = "half_day"
            elif current_hour > settings.start_work:
                # Kiểm tra grace period
                grace_minutes = timedelta(minutes=settings.late_arrival_grace_period_minutes)
                work_start_with_grace = datetime.combine(current_date, settings.start_work) + grace_minutes
                if current_time <= work_start_with_grace:
                    attendance_type = "normal"
                else:
                    attendance_type = "late"
            else:
                attendance_type = "normal"
        else:
            # Nếu time management disabled, luôn coi là normal
            attendance_type = "normal"

    elif "check-out" not in statuses:
        status = "check-out"
        checkin_log = next((r for r in records_today if r.status == "check-in"), None)
        if not checkin_log:
            return None, {"error": "Unexpected error: no check-in log found."}, 500

        # Kiểm tra minimum work hours nếu enabled
        if settings.enable_time_management and settings.enable_time_validation:
            time_diff = current_time - checkin_log.timestamp
            min_hours = timedelta(hours=settings.minimum_work_hours)
            if time_diff < min_hours:
                return None, {
                    "error": f"Cannot check out yet. Must wait at least {settings.minimum_work_hours} hours after check-in.",
                    "checked_in_at": format_time_vn(checkin_log.timestamp),
                    "minimum_checkout_time": format_time_vn(checkin_log.timestamp + min_hours)
                }, 400
        
        # Giữ nguyên attendance_type của check-in
        attendance_type = checkin_log.attendance_type if checkin_log else "normal"
    else:
        return {
            "message": "Already checked in and out today.",
            "records_today": [
                {
                    "status": r.status,
                    "attendance_type": r.attendance_type,
                    "timestamp": format_datetime_vn(r.timestamp)
                } for r in records_today
            ]
        }, None, 200

    # Ghi log chấm công
    try:
        attendance = Attendance.create_attendance(
            employee_id=employee_id,
            status=status,
            timestamp=current_time,
            attendance_type=attendance_type
        )
        db.session.add(attendance)
        db.session.commit()
        
        return {
            "message": "Attendance recorded successfully",
            "employee": {
                "employee_id": employee_id,
                "full_name": full_name,
                "department": department
            },
            "status": status,
            "attendance_type": attendance_type,
            "timestamp": format_datetime_vn(current_time)
        }, None, 200
    except Exception as e:
        db.session.rollback()
        return None, {"error": f"Failed to record attendance: {str(e)}"}, 500

def get_attendance_history_logic(employee_id):
    """Lấy lịch sử chấm công của nhân viên"""
    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return None, {"error": "Employee not found"}, 404
    
    records = Attendance.query.filter_by(employee_id=employee_id.upper())\
        .order_by(Attendance.timestamp.desc()).limit(50).all() # Giữ nguyên limit 50 hoặc làm pagination ở đây
    
    result = []
    for record in records:
        result.append({
            "attendance_id": record.attendance_id,
            "status": record.status,
            "attendance_type": record.attendance_type,
            "timestamp": format_datetime_vn(record.timestamp),
        })
    
    return {
        "employee": {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name
        },
        "records": result,
        "total": len(result)
    }, None, 200

def get_today_attendance_logic(employee_id):
    """Lấy chấm công hôm nay của nhân viên"""
    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return None, {"error": "Employee not found"}, 404
    
    records_today = Attendance.get_today_records(employee_id=employee_id.upper())
    
    result = []
    for record in records_today:
        result.append({
            "status": record.status,
            "attendance_type": record.attendance_type,
            "timestamp": format_datetime_vn(record.timestamp)
        })
    
    statuses = [r.status for r in records_today]
    if "check-in" not in statuses:
        current_status = "not_checked_in"
    elif "check-out" not in statuses:
        current_status = "checked_in"
    else:
        current_status = "completed"
    
    return {
        "employee": {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name
        },
        "current_status": current_status,
        "records_today": result,
        "total_records": len(result)
    }, None, 200

def capture_face_training_logic(image_file, base64_image, employee_id, pose_type):
    """Logic capture ảnh training cho nhân viên"""
    if not employee_id:
        return None, {"error": "Missing employee_id"}, 400
    if not image_file and not base64_image:
        return None, {"error": "No image provided"}, 400
    if not pose_type:
        return None, {"error": "Missing pose_type"}, 400

    # Validate pose_type
    try:
        FaceTrainingData.validate_pose_type(pose_type)
    except ValueError as e:
        return None, {"error": str(e)}, 400

    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return None, {"error": "Employee not found"}, 404

    # Đọc & chuẩn hóa ảnh
    try:
        if base64_image:
            if base64_image.startswith('data:'):
                base64_image = base64_image.split(',', 1)[1]
            raw_bytes = base64.b64decode(base64_image)
        else:
            raw_bytes = image_file.read()

        nparr = np.frombuffer(raw_bytes, np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_cv is None:
            return None, {"error": "Cannot decode image"}, 400

        ok, buf = cv2.imencode(".jpg", img_cv, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if not ok:
            return None, {"error": "Failed to encode image"}, 400
        image_data = BytesIO(buf.tobytes())
    except (base64.binascii.Error, ValueError) as e:
        return None, {"error": f"Image processing error: {str(e)}"}, 400

    # FIXED: Sinh face-encoding & metadata với employee_id
    success, message, encoding, metadata = (
        FacialRecognitionService.generate_face_encoding_with_metadata(
            image_data, 
            pose_type=pose_type,           # Named parameter
            employee_id=employee_id.upper()  # Named parameter - QUAN TRỌNG!
        )
    )
    if not success:
        return None, {"error": message}, 400

    # Lưu ảnh gốc
    try:
        image_data.seek(0)
        img_pil = Image.open(image_data).convert("RGB")
        save_dir = get_upload_path()
        os.makedirs(save_dir, exist_ok=True)
        # FIX: Sửa lỗi typo employeeid -> employee_id
        save_path = os.path.join(save_dir, f"{employee_id}_{metadata['pose_type']}.jpg")
        img_pil.save(save_path, quality=90)
    except Exception as e:
        return None, {"error": f"Save image failed: {str(e)}"}, 500

    # Ghi dữ liệu training
    try:
        # IMPROVED: Kiểm tra và thay thế pose existing nếu có
        existing_training = FaceTrainingData.query.filter_by(
            employee_id=employee_id.upper(), 
            pose_type=metadata['pose_type']
        ).first()
        
        if existing_training:
            # Cập nhật pose hiện có
            existing_training.face_encoding = encoding
            existing_training.image_quality_score = metadata['image_quality_score']
            existing_training.created_at = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
            print(f"Cập nhật pose {metadata['pose_type']} cho {employee_id}")
        else:
            # Tạo pose mới
            training_data = FaceTrainingData.create_training_data(
                employee_id=employee_id.upper(),
                pose_type=metadata['pose_type'],
                face_encoding=encoding,
                image_quality_score=metadata['image_quality_score']
            )
            db.session.add(training_data)
            print(f"Tạo pose mới {metadata['pose_type']} cho {employee_id}")
        
        db.session.commit()
        
        # Refresh progress sau khi commit
        updated_progress = employee.get_face_training_progress()
        
        # Log để debug
        print(f"Progress của {employee_id}: {updated_progress['poses_completed']}/{updated_progress['poses_required']} - Completed: {employee.face_training_completed}")
        
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return None, {"error": f"Database error: {str(e)}"}, 500

    return {
        "success": True,
        "message": "Pose captured successfully",
        "pose_type": metadata['pose_type'],
        "progress": updated_progress,
        "employee_id": employee_id.upper()
    }, None, 200