# backend/app/routes/attendance_report_routes.py

from flask import Blueprint, request, jsonify
from app.services.attendance_service import (
    recognize_face_logic,
    get_attendance_history_logic,
    get_today_attendance_logic,
    capture_face_training_logic
)

# Khởi tạo Blueprint cho các route chấm công
attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/api/recognize', methods=['POST'])
def recognize_face():
    """Nhận diện khuôn mặt và ghi nhận chấm công"""
    image_file = request.files.get('image')
    base64_image = request.form.get('base64_image')
    location = request.form.get('location')
    device_info = request.form.get('device_info')
    session_id = request.form.get('session_id') # THÊM DÒNG NÀY ĐỂ LẤY session_id TỪ REQUEST
    
    # THÊM session_id VÀO HÀM GỌI recognize_face_logic
    result, error, status = recognize_face_logic(image_file, base64_image, location, device_info, session_id)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@attendance_bp.route('/api/attendance/<string:employee_id>', methods=['GET'])
def get_attendance_history(employee_id):
    """Lấy lịch sử chấm công của nhân viên"""
    result, error, status = get_attendance_history_logic(employee_id)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@attendance_bp.route('/api/attendance/today/<string:employee_id>', methods=['GET'])
def get_today_attendance(employee_id):
    """Lấy chấm công hôm nay của nhân viên"""
    result, error, status = get_today_attendance_logic(employee_id)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@attendance_bp.route('/api/face-training/capture', methods=['POST'])
def capture_face_training():
    """Capture ảnh training cho nhân viên"""
    image_file = request.files.get('image')
    base64_image = request.form.get('base64_image')
    employee_id = request.form.get('employee_id')
    pose_type = request.form.get('pose_type')
    
    result, error, status = capture_face_training_logic(image_file, base64_image, employee_id, pose_type)
    if error:
        return jsonify(error), status
    return jsonify(result), status