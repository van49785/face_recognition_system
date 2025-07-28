# backend/app/routes/attendance_routes.py

from flask import Blueprint, request, jsonify
from app.services.attendance_service import (
    recognize_face_logic,
    get_attendance_history_logic,
    get_today_attendance_logic,
    capture_face_training_logic
)
from app.services.attendance_service import get_attendance_history_logic 
from app.utils.decorators import admin_required, employee_required # THÊM employee_required

# Khởi tạo Blueprint cho các route chấm công
attendance_bp = Blueprint('attendance_bp', __name__) # ĐỔI TÊN BIẾN TỪ 'attendance' THÀNH 'attendance_bp'

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
    # LƯU Ý: Route này hiện tại không yêu cầu xác thực. 
    # Nếu bạn muốn chỉ nhân viên đã đăng nhập mới xem được lịch sử của mình, 
    # bạn sẽ cần tạo một route riêng cho nhân viên và áp dụng @employee_required.
    # Route này có thể dùng cho Admin xem lịch sử của bất kỳ nhân viên nào.
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


@attendance_bp.route('/api/employee/attendance/history', methods=['GET'])
@employee_required # CHỈ NHÂN VIÊN ĐÃ ĐĂNG NHẬP MỚI ĐƯỢC XEM LỊCH SỬ CỦA CHÍNH HỌ
def get_current_employee_attendance_history():
    """Lấy lịch sử chấm công của nhân viên đang đăng nhập."""
    current_employee_id = request.current_user.employee_id # Lấy employee_id từ token đã xác thực
    
    # Có thể thêm các tham số query để lọc theo ngày/tháng
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    result, error, status = get_attendance_history_logic(current_employee_id)
    
    # Bạn có thể thêm logic lọc theo start_date/end_date vào get_attendance_history_logic
    # hoặc xử lý lọc ở đây nếu hàm logic chỉ trả về tất cả.
    # Hiện tại, get_attendance_history_logic không nhận start_date/end_date làm tham số
    # nên nó sẽ trả về 50 bản ghi gần nhất. Nếu muốn lọc, cần điều chỉnh hàm đó.

    if error:
        return jsonify(error), status
    return jsonify(result), status
