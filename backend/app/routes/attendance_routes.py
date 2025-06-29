from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import pytz

from app.services.facial_service import FacialRecognitionService
from app.services.attendance_service import record_attendance
from app.models.attendance import Attendance
from app.db import db
from app.utils.helpers import get_vn_datetime, format_datetime_vn, format_time_vn

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/api/recognize', methods=['POST'])
def recognize_face():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Nhận diện khuôn mặt
    success, message, processed_image = FacialRecognitionService.preprocess_image(image_file)
    if not success:
        return jsonify({"error": message}), 400

    success, message, employee = FacialRecognitionService.recognize_face_with_liveness(processed_image)
    if not success:
        return jsonify({"error": message}), 404

    employee_id = employee.employee_id
    full_name = employee.full_name
    department = employee.department
    
    # Lấy thời gian hiện tại theo timezone VN (consistent với models)
    current_time = get_vn_datetime()

    # Sử dụng method có sẵn từ Attendance model
    records_today = Attendance.get_today_records(employee_id=employee_id)
    
    # Lấy danh sách status hôm nay
    statuses = [r.status for r in records_today]

    # Logic xác định trạng thái
    if "check-in" not in statuses:
        # Chưa check-in hôm nay
        status = "check-in"
    elif "check-out" not in statuses:
        # Đã check-in rồi, kiểm tra thời gian để check-out
        checkin_log = next((r for r in records_today if r.status == "check-in"), None)
        if checkin_log:
            # So sánh naive datetime với naive datetime
            time_diff = current_time - checkin_log.timestamp
            if time_diff < timedelta(minutes=240):  # 4 giờ
                return jsonify({
                    "error": "Cannot check out yet. Must wait at least 4 hours after check-in.",
                    "checked_in_at": format_time_vn(checkin_log.timestamp),
                    "minimum_checkout_time": format_time_vn(checkin_log.timestamp + timedelta(minutes=240))
                }), 400
            status = "check-out"
        else:
            return jsonify({"error": "Unexpected error: no check-in log found."}), 500
    else:
        # Đã check-in và check-out rồi
        return jsonify({
            "message": "Already checked in and out today.",
            "records_today": [
                {
                    "status": r.status,
                    "timestamp": format_datetime_vn(r.timestamp)
                } for r in records_today
            ]
        }), 200

    # Ghi log chấm công
    try:
        # Sử dụng current_time thay vì UTC timestamp
        record_attendance(employee_id=employee_id, status=status, timestamp=current_time)
        
        return jsonify({
            "message": "Attendance recorded successfully",
            "employee": {
                "employee_id": employee_id,
                "full_name": full_name,
                "department": department
            },
            "status": status,
            "timestamp": format_datetime_vn(current_time)
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to record attendance: {str(e)}"}), 500

# API lấy lịch sử chấm công
@attendance_bp.route('/api/attendance/<string:employee_id>', methods=['GET'])
def get_attendance_history(employee_id):
    """Lấy lịch sử chấm công của nhân viên"""
    from app.models.employee import Employee
    
    # Kiểm tra nhân viên tồn tại
    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    # Lấy records (có thể thêm pagination sau)
    records = Attendance.query.filter_by(employee_id=employee_id.upper())\
        .order_by(Attendance.timestamp.desc()).limit(50).all()
    
    result = []
    for record in records:
        result.append({
            "attendance_id": record.attendance_id,
            "status": record.status,
            "timestamp": format_datetime_vn(record.timestamp),
            "location": record.location,
            "device_info": record.device_info
        })
    
    return jsonify({
        "employee": {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name
        },
        "records": result,
        "total": len(result)
    }), 200

# API lấy chấm công hôm nay
@attendance_bp.route('/api/attendance/today/<string:employee_id>', methods=['GET'])
def get_today_attendance(employee_id):
    """Lấy chấm công hôm nay của nhân viên"""
    from app.models.employee import Employee
    
    # Kiểm tra nhân viên tồn tại
    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    # Lấy records hôm nay
    records_today = Attendance.get_today_records(employee_id=employee_id.upper())
    
    result = []
    for record in records_today:
        result.append({
            "status": record.status,
            "timestamp": format_datetime_vn(record.timestamp),
            "location": record.location
        })
    
    # Xác định trạng thái hiện tại
    statuses = [r.status for r in records_today]
    if "check-in" not in statuses:
        current_status = "not_checked_in"
    elif "check-out" not in statuses:
        current_status = "checked_in"
    else:
        current_status = "completed"
    
    return jsonify({
        "employee": {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name
        },
        "current_status": current_status,
        "records_today": result,
        "total_records": len(result)
    }), 200