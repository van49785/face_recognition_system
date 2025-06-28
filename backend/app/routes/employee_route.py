# API nhân viên
from flask import Blueprint, request, jsonify, current_app
from app.services.facial_service import FacialRecognitionService
from app.models.employee import Employee
from app import db
from sqlalchemy.exc import IntegrityError
import pytz
import os
from io import BytesIO
from PIL import Image
from datetime import datetime
from app.utils.helpers import format_datetime_vn, get_upload_path

employee_bp = Blueprint('employee', __name__)

# Thêm nhân viên mới
@employee_bp.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.form
    image_file = request.files.get('image')

    required_fields = ['employee_id', 'full_name', 'department']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error":f"Missing required fields {field}"}), 400
    
    if not image_file:
        return jsonify({"error":"No image provided"}), 400
    
    employee_id = data['employee_id'].upper()

    # check trung ma nhan vien
    if Employee.query.filter_by(employee_id=employee_id).first():
        return jsonify({"error":"Employee ID already exits"}), 400
    
    # validate du lieu
    try:
        Employee.validate_email(data.get('email'))
        Employee.validate_phone(data.get('phone'))

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    
    # Encode khuôn mặt
    success, message, face_encoding = FacialRecognitionService.generate_face_encoding(image_file)
    if not success:
        return jsonify({"error": message}), 400
    
    # Lưu ảnh gốc vào thư mục local
    try:
        save_dir = get_upload_path()  # Sử dụng hàm nhất quán
        os.makedirs(save_dir, exist_ok=True)

        image_file.stream.seek(0)  # Reset pointer
        image = Image.open(BytesIO(image_file.read()))
        image = image.convert("RGB")  # Đảm bảo ảnh không bị lỗi kênh màu
        save_path = os.path.join(save_dir, f"{employee_id}.jpg")
        image.save(save_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save photo: {str(e)}"}), 500
    
    # Tạo nhân viên
    new_employee = Employee(
        employee_id = employee_id,
        full_name = data['full_name'],
        department = data['department'],
        position = data.get('position'),
        phone = data.get('phone'),
        email = data.get('email'),
        face_encoding = face_encoding,
        status = True
    )

    try:
        db.session.add(new_employee)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error – possibly duplicate or constraint violation"}), 500

    return jsonify({
        "message": "Employee added successfully",
        "employee": {
            "employee_id": new_employee.employee_id,
            "full_name": new_employee.full_name,
            "department": new_employee.department
        }
    }), 201

# Lấy tất cả nhân viên
@employee_bp.route('/api/employees', methods=['GET'])
def get_all_active_employees():
    employees = Employee.query.filter_by(status=True).order_by(Employee.created_at.desc()).all()

    result = []
    for emp in employees:
        result.append({
            "employee_id": emp.employee_id,
            "full_name": emp.full_name,
            "department": emp.department,
            "position": emp.position,
            "created_at": format_datetime_vn(emp.created_at)
        })

    return jsonify({
        "employees": result,
        "total": len(result)
    }), 200

# Xem chi tiết thông tin của một nhân viên
@employee_bp.route('/api/employees/<string:employee_id>', methods=['GET'])
def get_employee_detail(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    return jsonify({
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "department": employee.department,
        "position": employee.position,
        "phone": employee.phone,
        "email": employee.email,
        "status": "active" if employee.status else "inactive",
        "created_at": format_datetime_vn(employee.created_at),
        "updated_at": format_datetime_vn(employee.updated_at)
    }), 200

# Update nhân viên
@employee_bp.route('/api/employees/<string:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.form
    image_file = request.files.get('image')

    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    # Cập nhật các trường nếu có
    if data.get("full_name"):
        employee.full_name = data["full_name"]
    if data.get("department"):
        employee.department = data["department"]
    if data.get("position"):
        employee.position = data["position"]
    if data.get("phone"):
        try:
            Employee.validate_phone(data["phone"])
            employee.phone = data["phone"]
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
    if data.get("email"):
        try:
            Employee.validate_email(data["email"])
            employee.email = data["email"]
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400

    # Nếu có ảnh mới → sinh lại face_encoding
    if image_file:
        success, message, face_encoding = FacialRecognitionService.generate_face_encoding(image_file)
        if not success:
            return jsonify({"error": message}), 400
        employee.face_encoding = face_encoding
        
        # Lưu ảnh mới với đường dẫn nhất quán
        try:
            save_dir = get_upload_path()  # Sử dụng hàm nhất quán
            os.makedirs(save_dir, exist_ok=True)
            
            image_file.stream.seek(0)
            image = Image.open(BytesIO(image_file.read()))
            image = image.convert("RGB")
            save_path = os.path.join(save_dir, f"{employee.employee_id}.jpg")
            image.save(save_path)
        except Exception as e:
            # Log error but don't fail the request since DB is already updated
            print(f"Warning: Failed to save updated photo: {str(e)}")

    db.session.commit()

    return jsonify({
        "message": "Employee updated successfully",
        "employee": {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
            "department": employee.department,
            "position": employee.position
        }
    }), 200

# Xoá mềm nhân viên status = False
@employee_bp.route('/api/employees/<string:employee_id>', methods=['DELETE'])
def soft_delete_employee(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    if not employee.status:
        return jsonify({"message": "Employee is already inactive"}), 200

    employee.status = False
    db.session.commit()

    return jsonify({
        "message": "Employee soft-deleted successfully",
        "employee_id": employee.employee_id,
        "full_name": employee.full_name
    }), 200