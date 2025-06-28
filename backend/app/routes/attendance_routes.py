from flask import Blueprint, request, jsonify
from datetime import datetime, time, timedelta, timezone
import pytz

from app.services.facial_service import FacialRecognitionService
from app.services.attendance_service import record_attendance
from app.models.attendance import Attendance
from app.db import db

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
    timestamp = datetime.now(timezone.utc)
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    local_time = timestamp.astimezone(vn_tz)

    # Kiểm tra log hôm nay
    today = local_time.date()
    start_of_day = datetime.combine(today, time.min).astimezone(vn_tz)
    end_of_day = datetime.combine(today, time.max).astimezone(vn_tz)

    records_today = Attendance.query.filter_by(employee_id=employee_id)\
        .filter(Attendance.timestamp >= start_of_day)\
        .filter(Attendance.timestamp <= end_of_day)\
        .order_by(Attendance.timestamp.asc()).all()

    statuses = [r.status for r in records_today]

    if "check-in" not in statuses:
        status = "check-in"
    elif "check-out" not in statuses:
        # Đã check-in rồi, kiểm tra thời gian
        checkin_log = next((r for r in records_today if r.status == "check-in"), None)
        if checkin_log:
            delta = local_time - checkin_log.timestamp.astimezone(vn_tz)
            if delta < timedelta(minutes=240):
                return jsonify({
                    "error": "Cannot check out yet. Must wait at least 4 hours after check-in.",
                    "checked_in_at": checkin_log.timestamp.astimezone(vn_tz).strftime("%H:%M:%S")
                }), 400
            status = "check-out"
        else:
            return jsonify({"error": "Unexpected error: no check-in log found."}), 500
    else:
        return jsonify({"message": "Already checked in and out today."}), 200

    # Ghi log
    record_attendance(employee_id=employee_id, status=status, timestamp=timestamp)

    return jsonify({
        "message": "Attendance recorded successfully",
        "employee": {
            "employee_id": employee_id,
            "full_name": full_name
        },
        "status": status,
        "timestamp": local_time.strftime("%d/%m/%Y %H:%M:%S")
    }), 200
