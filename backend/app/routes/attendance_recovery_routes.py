# app/routes/attendance_recovery_routes.py
from flask import Blueprint, request, jsonify
from app.services.attendance_recovery_service import AttendanceRecoveryService
from app.utils.decorators import employee_required, admin_required # Import decorators
from datetime import datetime

attendance_recovery_bp = Blueprint('attendance_recovery_bp', __name__)

# --- ROUTES CHO NHÂN VIÊN ---

@attendance_recovery_bp.route('/api/employee/attendance/recovery/submit', methods=['POST'])
@employee_required # Chỉ nhân viên đã đăng nhập mới được gửi yêu cầu
def submit_employee_recovery_request():
    data = request.get_json(silent=True) or {}
    request_date = data.get('request_date') # Định dạng YYYY-MM-DD
    reason = data.get('reason')
    
    # request.current_user được đặt bởi decorator @employee_required
    current_employee_id = request.current_user.employee_id 

    if not request_date or not reason:
        return jsonify({"error": "Date and recovery reason are required."}), 400

    success, message = AttendanceRecoveryService.submit_recovery_request(
        current_employee_id, request_date, reason
    )
    if not success:
        return jsonify({"error": message}), 400
    return jsonify({"message": message}), 201

@attendance_recovery_bp.route('/api/employee/attendance/recovery/my-requests', methods=['GET'])
@employee_required # Chỉ nhân viên đã đăng nhập mới được xem yêu cầu của mình
def get_my_recovery_requests():
    current_employee_id = request.current_user.employee_id
    requests = AttendanceRecoveryService.get_employee_recovery_requests(current_employee_id)
    return jsonify({"requests": requests}), 200

# --- ROUTES CHO ADMIN ---

@attendance_recovery_bp.route('/api/admin/attendance/recovery/pending', methods=['GET'])
@admin_required # Chỉ Admin mới được xem các yêu cầu đang chờ
def get_pending_recovery_requests():
    requests = AttendanceRecoveryService.get_all_pending_recovery_requests()
    return jsonify({"pending_requests": requests}), 200

@attendance_recovery_bp.route('/api/admin/attendance/recovery/process/<string:request_id>', methods=['POST'])
@admin_required # Chỉ Admin mới được xử lý yêu cầu
def process_attendance_recovery(request_id):
    data = request.get_json(silent=True) or {}
    status = data.get('status') # 'approved' hoặc 'rejected'
    notes = data.get('notes')
    
    # request.current_user được đặt bởi decorator @admin_required
    current_admin_id = request.current_user.id 

    if status not in ['approved', 'rejected']:
        return jsonify({"error": "Invalid status. Only 'approved' or 'rejected' are accepted."}), 400

    success, message = AttendanceRecoveryService.process_recovery_request(
        request_id, current_admin_id, status, notes
    )
    if not success:
        return jsonify({"error": message}), 400
    return jsonify({"message": message}), 200