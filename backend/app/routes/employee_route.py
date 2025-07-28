# backend/app/routes/employee_routes.py

from flask import Blueprint, request, jsonify
from app.services.employee_service import (
    serve_uploaded_image_logic,
    add_employee_logic,
    get_employees_logic,
    get_employee_detail_logic,
    update_employee_logic,
    soft_delete_employee_logic,
    restore_employee_logic,
    set_employee_password_logic # THÊM IMPORT NÀY
)
from app.utils.decorators import admin_required # THÊM IMPORT NÀY

# Khởi tạo Blueprint cho các route liên quan đến employee
employee_bp = Blueprint('employee_bp', __name__) # ĐỔI TÊN BIẾN TỪ 'employee' THÀNH 'employee_bp'

@employee_bp.route('/Uploads/<path:filename>')
def serve_uploaded_image(filename):
    """Phục vụ ảnh từ thư mục uploads"""
    result, error, status = serve_uploaded_image_logic(filename)
    if error:
        return jsonify(error), status
    return result

@employee_bp.route('/api/employees', methods=['POST'])
@admin_required # CHỈ ADMIN MỚI ĐƯỢC THÊM NHÂN VIÊN
def add_employee():
    """Thêm nhân viên mới với thông tin và ảnh khuôn mặt"""
    data = request.form
    image_files = request.files.getlist('images')
    result, error, status = add_employee_logic(data, image_files)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees', methods=['GET'])
@admin_required # CHỈ ADMIN MỚI ĐƯỢC XEM DANH SÁCH NHÂN VIÊN
def get_employees():
    """Lấy danh sách nhân viên với pagination và search"""
    # Lấy parameters
    status_param = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    result, error, status = get_employees_logic(
        status_param=status_param,
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees/<string:employee_id>', methods=['GET'])
@admin_required # CHỈ ADMIN MỚI ĐƯỢC XEM CHI TIẾT NHÂN VIÊN
def get_employee_detail(employee_id):
    """Lấy thông tin chi tiết của một nhân viên theo employee_id"""
    result, error, status = get_employee_detail_logic(employee_id)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees/<string:employee_id>', methods=['PUT'])
@admin_required # CHỈ ADMIN MỚI ĐƯỢC CẬP NHẬT NHÂN VIÊN
def update_employee(employee_id):
    """Cập nhật thông tin nhân viên hoặc ảnh khuôn mặt"""
    data = request.form
    image_files = request.files.getlist('images')
    result, error, status = update_employee_logic(employee_id, data, image_files)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees/<string:employee_id>', methods=['DELETE'])
@admin_required # CHỈ ADMIN MỚI ĐƯỢC XÓA MỀM NHÂN VIÊN
def soft_delete_employee(employee_id):
    """Đánh dấu nhân viên là inactive (xóa mềm)"""
    result, error, status = soft_delete_employee_logic(employee_id)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees/<string:employee_id>/restore', methods=['PUT'])
@admin_required # CHỈ ADMIN MỚI ĐƯỢC KHÔI PHỤC NHÂN VIÊN
def restore_employee(employee_id):
    """Khôi phục nhân viên từ trạng thái inactive"""
    result, error, status = restore_employee_logic(employee_id)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees/<string:employee_id>/set-password', methods=['POST'])
@admin_required # CHỈ ADMIN MỚI ĐƯỢC ĐẶT LẠI MẬT KHẨU
def set_employee_password_route(employee_id):
    data = request.get_json(silent=True) or {}
    new_password = data.get('new_password')
    username = data.get('username') # Admin có thể tùy chọn đặt username khác

    if not new_password:
        return jsonify({"error": "Password canot be empty"}), 400

    result, error, status = set_employee_password_logic(employee_id, new_password, username)
    if error:
        return jsonify(error), status
    return jsonify(result), status



