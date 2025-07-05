# backend/app/routes/employee_routes.py

from flask import Blueprint, request, jsonify
from app.services.employee_service import (
    serve_uploaded_image_logic,
    add_employee_logic,
    get_employees_logic,
    get_employee_detail_logic,
    update_employee_logic,
    soft_delete_employee_logic,
    restore_employee_logic
)

# Khởi tạo Blueprint cho các route liên quan đến employee
employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/Uploads/<path:filename>')
def serve_uploaded_image(filename):
    """Phục vụ ảnh từ thư mục uploads"""
    result, error, status = serve_uploaded_image_logic(filename)
    if error:
        return jsonify(error), status
    return result

@employee_bp.route('/api/employees', methods=['POST'])
def add_employee():
    """Thêm nhân viên mới với thông tin và ảnh khuôn mặt"""
    data = request.form
    image_files = request.files.getlist('images')
    result, error, status = add_employee_logic(data, image_files)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees', methods=['GET'])
def get_employees():
    """Lấy danh sách nhân viên, có thể lọc theo trạng thái"""
    status_param = request.args.get('status')
    result, error, status = get_employees_logic(status_param)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees/<string:employee_id>', methods=['GET'])
def get_employee_detail(employee_id):
    """Lấy thông tin chi tiết của một nhân viên theo employee_id"""
    result, error, status = get_employee_detail_logic(employee_id)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees/<string:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """Cập nhật thông tin nhân viên hoặc ảnh khuôn mặt"""
    data = request.form
    image_files = request.files.getlist('images')
    result, error, status = update_employee_logic(employee_id, data, image_files)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees/<string:employee_id>', methods=['DELETE'])
def soft_delete_employee(employee_id):
    """Đánh dấu nhân viên là inactive (xóa mềm)"""
    result, error, status = soft_delete_employee_logic(employee_id)
    if error:
        return jsonify(error), status
    return jsonify(result), status

@employee_bp.route('/api/employees/<string:employee_id>/restore', methods=['PUT'])
def restore_employee(employee_id):
    """Khôi phục nhân viên từ trạng thái inactive"""
    result, error, status = restore_employee_logic(employee_id)
    if error:
        return jsonify(error), status
    return jsonify(result), status