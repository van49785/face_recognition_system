# API nhân viên
from flask import Blueprint, request, jsonify, current_app, send_from_directory 
from app.services.facial_service import FacialRecognitionService
from app.models.employee import Employee
from app.models.attendance import Attendance
from app import db
from sqlalchemy.exc import IntegrityError
import pytz
import os
from io import BytesIO
from PIL import Image 
from datetime import datetime, timezone 
from app.utils.helpers import format_datetime_vn, get_upload_path

employee_bp = Blueprint('employee', __name__)

# Helper function để serialize dữ liệu nhân viên một cách đầy đủ cho danh sách
# và cho các phản hồi thêm/sửa để đồng nhất dữ liệu frontend.
def serialize_employee_full(employee):
    image_filename = f"{employee.employee_id}.jpg"
    image_path_on_disk = os.path.join(get_upload_path(), image_filename)
    
    # URL ảnh sẽ là /uploads/ thay vì /static/faces/
    # Backend sẽ phục vụ file này thông qua route custom dưới đây
    image_url = f"/uploads/{image_filename}" if os.path.exists(image_path_on_disk) else None

    return {
        "id": employee.id,
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "department": employee.department,
        "position": employee.position,
        "phone": employee.phone, 
        "email": employee.email, 
        "status": employee.status, # Trả về boolean status
        "created_at": format_datetime_vn(employee.created_at),
        "updated_at": format_datetime_vn(employee.updated_at),
        "imageUrl": image_url # Sử dụng URL mới
    }

# Route để phục vụ các file ảnh từ thư mục 'data/uploads'
# Chúng ta định nghĩa nó trong employee_bp để nó được quản lý cùng các route nhân viên
@employee_bp.route('/uploads/<path:filename>')
def serve_uploaded_image(filename):
    upload_folder = get_upload_path() # Lấy đường dẫn đã được xác định trong helpers.py
    print(f"DEBUG: Attempting to serve '{filename}' from physical path: '{upload_folder}'") # <-- THÊM DÒNG NÀY
    try:
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        print(f"ERROR: Failed to send file {filename} from {upload_folder}: {e}")
        return jsonify({"error": "File not found or cannot be served"}), 404


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
        save_dir = get_upload_path() 
        os.makedirs(save_dir, exist_ok=True)

        image_file.stream.seek(0) 
        image = Image.open(BytesIO(image_file.read()))
        image = image.convert("RGB")
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
        "employee": serialize_employee_full(new_employee) 
    }), 201

# Lấy danh sách nhân viên (có thể lọc theo status)
@employee_bp.route('/api/employees', methods=['GET'])
def get_employees(): 
    status_param = request.args.get('status') 

    query = Employee.query
    if status_param:
        if status_param.lower() == 'active':
            query = query.filter_by(status=True)
        elif status_param.lower() == 'inactive':
            query = query.filter_by(status=False)
    
    employees = query.order_by(Employee.created_at.desc()).all()

    result = []
    for emp in employees:
        result.append(serialize_employee_full(emp)) 

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
    
    return jsonify({"employee": serialize_employee_full(employee)}), 200

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
    if data.get("phone") is not None: 
        try:
            Employee.validate_phone(data["phone"])
            employee.phone = data["phone"]
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
    if data.get("email") is not None: 
        try:
            Employee.validate_email(data["email"])
            employee.email = data["email"]
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
    if data.get("status") is not None: 
        employee.status = data["status"].lower() == 'true'

    # Nếu có ảnh mới → sinh lại face_encoding
    if image_file:
        success, message, face_encoding = FacialRecognitionService.generate_face_encoding(image_file)
        if not success:
            return jsonify({"error": message}), 400
        employee.face_encoding = face_encoding
        
        # Lưu ảnh mới với đường dẫn nhất quán
        try:
            save_dir = get_upload_path() 
            os.makedirs(save_dir, exist_ok=True)
            
            image_file.stream.seek(0)
            image = Image.open(BytesIO(image_file.read()))
            image = image.convert("RGB")
            save_path = os.path.join(save_dir, f"{employee.employee_id}.jpg")
            image.save(save_path)
        except Exception as e:
            print(f"Warning: Failed to save updated photo: {str(e)}")
 
    employee.updated_at = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
    employee.updated_at = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)

    db.session.commit()

    return jsonify({
        "message": "Employee updated successfully",
        "employee": serialize_employee_full(employee) 
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
    employee.updated_at = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
    employee.updated_at = datetime.now(timezone.utc) 
    db.session.commit()

    return jsonify({
        "message": "Employee soft-deleted successfully",
        "employee": serialize_employee_full(employee) 
    }), 200

# Endpoint để khôi phục nhân viên (chuyển status từ False về True)
@employee_bp.route('/api/employees/<string:employee_id>/restore', methods=['PUT'])
def restore_employee(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    if employee.status: 
        return jsonify({"message": "Employee is already active"}), 200

    employee.status = True 
    employee.updated_at = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
    db.session.commit()

    return jsonify({
        "message": f"Employee {employee_id} restored successfully",
        "employee": serialize_employee_full(employee) 
    }), 200
