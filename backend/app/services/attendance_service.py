# backend/app/utils/attendance_utils.py # Lưu ý: Đây là comment trong file, tên file thực tế là attendance_service.py

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
from app.utils.helpers import get_vn_datetime, format_datetime_vn, format_time_vn, get_upload_path

def recognize_face_logic(image_file, base64_image, location, device_info, session_id: str): # THÊM session_id VÀO ĐÂY
    """Logic nhận diện khuôn mặt và ghi nhận chấm công"""
    # Kiểm tra đầu vào
    if not image_file and not base64_image:
        return None, {"error": "No image provided"}, 400

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

    # Nhận diện khuôn mặt (Đã thêm session_id vào đây)
    success, message, employee = FacialRecognitionService.recognize_face_with_liveness(image, session_id)
    if not success:
        return None, {"error": message}, 400
    if not employee:
        return None, {"error": "Employee not found from face recognition"}, 404

    employee_id = employee.employee_id
    full_name = employee.full_name
    department = employee.department

    # Lấy thời gian & cài đặt chấm công
    current_time = get_vn_datetime()
    current_date = current_time.date()
    current_hour = current_time.time()

    start_work = time(8, 30)
    checkin_start = time(7, 0)
    checkin_late_end = time(9, 0)
    half_day_start = time(12, 0)
    half_day_end = time(13, 30)

    # Lấy log chấm công hôm nay
    records_today = Attendance.get_today_records(employee_id=employee_id)
    statuses = [r.status for r in records_today]

    # Ngăn chấm công trùng
    if statuses.count("check-in") > 1 or statuses.count("check-out") > 1:
        return None, {
            "error": "Multiple check-in or check-out detected today. Please contact admin."
        }, 400

    # Xác định trạng thái
    if "check-in" not in statuses:
        # --- START: Logic kiểm tra thời gian check-in TẠM THỜI VÔ HIỆU HÓA ---
        # if current_hour < checkin_start:
        #     return None, {
        #         "error": "Check-in not allowed before 7:00",
        #         "next_valid_time": format_time_vn(datetime.combine(current_date, checkin_start))
        #     }, 400
        # elif current_hour > checkin_late_end:
        #     return None, {"error": "Check-in not allowed after 9:00"}, 400
        # elif half_day_start <= current_hour <= half_day_end:
        #     status = "check-in"
        #     attendance_type = "half_day"
        # elif current_hour > start_work:
        #     status = "check-in"
        #     attendance_type = "late"
        # else:
        #     status = "check-in"
        #     attendance_type = "normal"
        # --- END: Logic kiểm tra thời gian check-in TẠM THỜI VÔ HIỆU HÓA ---

        # Logic MỚI (để test): Luôn coi là check-in bình thường
        status = "check-in"
        attendance_type = "normal" # Mặc định là normal để dễ test

    elif "check-out" not in statuses:
        checkin_log = next((r for r in records_today if r.status == "check-in"), None)
        if not checkin_log:
            return None, {"error": "Unexpected error: no check-in log found."}, 500

        # --- START: Logic kiểm tra thời gian check-out TẠM THỜI VÔ HIỆU HÓA ---
        # time_diff = current_time - checkin_log.timestamp
        # if time_diff < timedelta(hours=4):
        #     return None, {
        #         "error": "Cannot check out yet. Must wait at least 4 hours after check-in.",
        #         "checked_in_at": format_time_vn(checkin_log.timestamp),
        #         "minimum_checkout_time": format_time_vn(checkin_log.timestamp + timedelta(hours=4))
        #     }, 400
        # --- END: Logic kiểm tra thời gian check-out TẠM THỜI VÔ HIỆU HÓA ---
        
        # Logic MỚI (để test): Luôn coi là check-out bình thường
        status = "check-out"
        # Giữ nguyên attendance_type của check-in nếu có, hoặc mặc định normal
        attendance_type = checkin_log.attendance_type if checkin_log else "normal"
        # attendance_type = "half_day" if half_day_start <= current_hour <= half_day_end else checkin_log.attendance_type # Dòng cũ
    else:
        # Giữ nguyên phần này
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
        .order_by(Attendance.timestamp.desc()).limit(50).all()
    
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

    # Sinh face-encoding & metadata
    success, message, encoding, metadata = (
        FacialRecognitionService.generate_face_encoding_with_metadata(image_data, pose_type)
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
        training_data = FaceTrainingData.create_training_data(
            employee_id=employee_id,
            pose_type=metadata['pose_type'],
            face_encoding=encoding,
            image_quality_score=metadata['image_quality_score']
        )
        db.session.add(training_data)

        # Kiểm tra progress và update employee status
        current_progress = employee.get_face_training_progress()
        if current_progress['poses_completed'] >= 3:
            employee.complete_face_training()

        db.session.commit()
        
        # Refresh progress sau khi commit
        updated_progress = employee.get_face_training_progress()
        
    except Exception as e:
        db.session.rollback()
        return None, {"error": f"Database error: {str(e)}"}, 500

    return {
        "success": True,
        "message": "Pose captured successfully",
        "pose_type": metadata['pose_type'],
        "progress": updated_progress,
        "employee_id": employee_id
    }, None, 200