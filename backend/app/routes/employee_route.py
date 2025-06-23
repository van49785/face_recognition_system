# API nhân viên
from flask import Blueprint, request, jsonify
from app.services.facial_service import FacialRecognitionService
from app.models.employee import Employee
from app import db

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/api/employees', methods=['POST'])
def add_employee():
    if 'image' not in request.files:
        return jsonify({"error":"No image provided"}), 400
    
    image_file = request.files['image']
    success, message, face_encoding = FacialRecognitionService.generate_face_encoding(image_file)

    if not success:
        return jsonify({"error": message}), 400
    
    employee = Employee(
        employee_id = request.form['employee_id'],
        full_name = request.form['full_name'],
        face_encoding= face_encoding
    )

    db.session.add(employee)
    db.session.commit()
    return jsonify({"message": "Employee added successfully"}), 201