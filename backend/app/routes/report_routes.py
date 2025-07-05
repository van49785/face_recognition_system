# API báo cáo
# backend/app/routes/attendance_report_routes.py

from flask import Blueprint, request, jsonify
from app.services.report_service import get_date_range, get_employee_report, get_department_report, get_company_report, export_to_excel

# Khởi tạo Blueprint cho báo cáo
report_bp = Blueprint('reports', __name__)

@report_bp.route('/api/reports/employee/<string:employee_id>', methods=['GET'])
def employee_report(employee_id):
    """Báo cáo chấm công của một nhân viên"""
    start_date, end_date, error, status = get_date_range(request.args)
    if error:
        return jsonify(error), status
    
    result, error, status = get_employee_report(employee_id, start_date, end_date)
    if error:
        return jsonify(error), status
    return jsonify(result), 200

@report_bp.route('/api/reports/department/<string:department>', methods=['GET'])
def department_report(department):
    """Báo cáo chấm công của một phòng ban"""
    start_date, end_date, error, status = get_date_range(request.args)
    if error:
        return jsonify(error), status
    
    result, error, status = get_department_report(department, start_date, end_date)
    if error:
        return jsonify(error), status
    return jsonify(result), 200

@report_bp.route('/api/reports/company', methods=['GET'])
def company_report():
    """Báo cáo chấm công toàn công ty"""
    start_date, end_date, error, status = get_date_range(request.args)
    if error:
        return jsonify(error), status
    
    result, error, status = get_company_report(start_date, end_date)
    if error:
        return jsonify(error), status
    return jsonify(result), 200

@report_bp.route('/api/reports/export/<string:report_type>', methods=['GET'])
def export_report(report_type):
    """Xuất báo cáo ra file Excel"""
    start_date, end_date, error, status = get_date_range(request.args)
    if error:
        return jsonify(error), status
    
    result, error, status = export_to_excel(report_type, start_date, end_date)
    if error:
        return jsonify(error), status
    return jsonify(result), 200