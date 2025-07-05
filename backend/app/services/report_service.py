from datetime import datetime, time
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, Alignment
import os
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.utils.helpers import get_vn_datetime, format_datetime_vn, get_export_path
from sqlalchemy import and_

def calculate_work_hours(checkin_time, checkout_time):
    """Tính số giờ làm việc giữa check-in và check-out"""
    if checkin_time and checkout_time:
        # Đảm bảo checkout_time > checkin_time
        if checkout_time > checkin_time:
            delta = checkout_time - checkin_time
            return delta.total_seconds() / 3600
        else:
            # Trường hợp checkout_time <= checkin_time (có thể do lỗi dữ liệu)
            return 0
    return 0

def get_date_range(args):
    """Lấy khoảng thời gian từ query params, mặc định là tháng hiện tại"""
    start_date = args.get('start_date')
    end_date = args.get('end_date')
    vn_now = get_vn_datetime()
    
    # Mặc định là từ đầu tháng đến cuối tháng hiện tại
    default_start = vn_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Tìm ngày cuối tháng
    if vn_now.month == 12:
        next_month = vn_now.replace(year=vn_now.year + 1, month=1, day=1)
    else:
        next_month = vn_now.replace(month=vn_now.month + 1, day=1)
    default_end = (next_month - datetime.timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
    
    try:
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start = default_start
            
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            end = default_end
            
        # Validate date range
        if start > end:
            return None, None, {"error": "Start date must be before end date"}, 400
            
    except ValueError:
        return None, None, {"error": "Invalid date format. Use YYYY-MM-DD"}, 400
    
    return start, end, None, None

def process_employee_attendance(employee_id, start_date, end_date):
    """Xử lý dữ liệu chấm công của một nhân viên - hàm dùng chung"""
    records = Attendance.query.filter(
        and_(
            Attendance.employee_id == employee_id.upper(),
            Attendance.timestamp >= start_date,
            Attendance.timestamp <= end_date
        )
    ).order_by(Attendance.timestamp.asc()).all()
    
    report = {
        "normal_days": 0,
        "late_days": 0,
        "half_days": 0,
        "total_work_hours": 0,
        "total_attendance_days": 0  # Thêm tổng số ngày có mặt
    }
    
    daily_records = defaultdict(list)
    
    for record in records:
        day = record.timestamp.date()
        daily_records[day].append(record)
    
    for day, day_records in daily_records.items():
        # Sắp xếp theo thời gian
        day_records.sort(key=lambda x: x.timestamp)
        
        checkin = next((r for r in day_records if r.status == "check-in"), None)
        checkout = next((r for r in day_records if r.status == "check-out"), None)
        
        if checkin:
            report["total_attendance_days"] += 1
            attendance_type = checkin.attendance_type
            
            if attendance_type == "normal":
                report["normal_days"] += 1
            elif attendance_type == "late":
                report["late_days"] += 1
            elif attendance_type == "half_day":
                report["half_days"] += 1
                
            # Tính giờ làm việc chỉ khi có cả check-in và check-out
            if checkout:
                work_hours = calculate_work_hours(checkin.timestamp, checkout.timestamp)
                report["total_work_hours"] += work_hours
    
    # Làm tròn tổng giờ làm việc
    report["total_work_hours"] = round(report["total_work_hours"], 2)
    
    return report

def get_employee_report(employee_id, start_date, end_date):
    """Lấy báo cáo chấm công của một nhân viên"""
    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return None, {"error": "Employee not found"}, 404
    
    # Kiểm tra nhân viên có active không
    if not employee.status:
        return None, {"error": "Employee is inactive"}, 400
    
    records = Attendance.query.filter(
        and_(
            Attendance.employee_id == employee_id.upper(),
            Attendance.timestamp >= start_date,
            Attendance.timestamp <= end_date
        )
    ).order_by(Attendance.timestamp.asc()).all()
    
    report = process_employee_attendance(employee_id, start_date, end_date)
    
    # Thêm chi tiết từng bản ghi
    detailed_records = []
    for record in records:
        detailed_records.append({
            "date": record.timestamp.strftime("%Y-%m-%d"),
            "time": record.timestamp.strftime("%H:%M:%S"),
            "status": record.status,
            "attendance_type": record.attendance_type,
            "timestamp": format_datetime_vn(record.timestamp),
            "location": record.location
        })
    
    report["records"] = detailed_records
    
    return {
        "employee": {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
            "department": employee.department,
            "position": employee.position
        },
        "report": report,
        "period": {
            "start_date": format_datetime_vn(start_date),
            "end_date": format_datetime_vn(end_date)
        }
    }, None, None

def get_department_report(department, start_date, end_date):
    """Lấy báo cáo chấm công của một phòng ban"""
    employees = Employee.query.filter_by(department=department, status=True).all()
    if not employees:
        return None, {"error": "No active employees found in this department"}, 404
    
    total_report = {
        "total_normal_days": 0,
        "total_late_days": 0,
        "total_half_days": 0,
        "total_work_hours": 0,
        "total_attendance_days": 0,
        "employee_reports": []
    }
    
    for employee in employees:
        employee_report = process_employee_attendance(employee.employee_id, start_date, end_date)
        
        employee_data = {
            "employee_id": employee.employee_id,
            "full_name": employee.full_name,
            "position": employee.position,
            **employee_report
        }
        
        total_report["employee_reports"].append(employee_data)
        
        # Cộng dồn vào tổng
        total_report["total_normal_days"] += employee_report["normal_days"]
        total_report["total_late_days"] += employee_report["late_days"]
        total_report["total_half_days"] += employee_report["half_days"]
        total_report["total_work_hours"] += employee_report["total_work_hours"]
        total_report["total_attendance_days"] += employee_report["total_attendance_days"]
    
    total_report["total_work_hours"] = round(total_report["total_work_hours"], 2)
    
    return {
        "department": department,
        "total_employees": len(employees),
        "report": total_report,
        "period": {
            "start_date": format_datetime_vn(start_date),
            "end_date": format_datetime_vn(end_date)
        }
    }, None, None

def get_company_report(start_date, end_date):
    """Lấy báo cáo chấm công toàn công ty"""
    employees = Employee.query.filter_by(status=True).all()
    if not employees:
        return None, {"error": "No active employees found"}, 404
    
    company_report = {
        "total_normal_days": 0,
        "total_late_days": 0,
        "total_half_days": 0,
        "total_work_hours": 0,
        "total_attendance_days": 0,
        "department_reports": defaultdict(lambda: {
            "normal_days": 0,
            "late_days": 0,
            "half_days": 0,
            "total_work_hours": 0,
            "total_attendance_days": 0,
            "employee_count": 0
        })
    }
    
    for employee in employees:
        employee_report = process_employee_attendance(employee.employee_id, start_date, end_date)
        
        # Cộng dồn vào tổng công ty
        company_report["total_normal_days"] += employee_report["normal_days"]
        company_report["total_late_days"] += employee_report["late_days"]
        company_report["total_half_days"] += employee_report["half_days"]
        company_report["total_work_hours"] += employee_report["total_work_hours"]
        company_report["total_attendance_days"] += employee_report["total_attendance_days"]
        
        # Cộng dồn vào phòng ban
        dept_report = company_report["department_reports"][employee.department]
        dept_report["normal_days"] += employee_report["normal_days"]
        dept_report["late_days"] += employee_report["late_days"]
        dept_report["half_days"] += employee_report["half_days"]
        dept_report["total_work_hours"] += employee_report["total_work_hours"]
        dept_report["total_attendance_days"] += employee_report["total_attendance_days"]
        dept_report["employee_count"] += 1
    
    company_report["total_work_hours"] = round(company_report["total_work_hours"], 2)
    
    # Chuyển đổi department_reports thành list
    department_reports = []
    for dept, stats in company_report["department_reports"].items():
        stats["total_work_hours"] = round(stats["total_work_hours"], 2)
        department_reports.append({"department": dept, **stats})
    
    return {
        "report": {
            "total_employees": len(employees),
            "total_normal_days": company_report["total_normal_days"],
            "total_late_days": company_report["total_late_days"],
            "total_half_days": company_report["total_half_days"],
            "total_work_hours": company_report["total_work_hours"],
            "total_attendance_days": company_report["total_attendance_days"],
            "department_reports": department_reports
        },
        "period": {
            "start_date": format_datetime_vn(start_date),
            "end_date": format_datetime_vn(end_date)
        }
    }, None, None

def export_to_excel(report_type, start_date, end_date):
    """Xuất báo cáo ra file Excel"""
    data = []
    
    try:
        if report_type.startswith('employee/'):
            employee_id = report_type.split('/')[1].upper()
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if not employee:
                return None, {"error": "Employee not found"}, 404
            
            if not employee.status:
                return None, {"error": "Employee is inactive"}, 400
            
            report = process_employee_attendance(employee_id, start_date, end_date)
            
            data.append({
                "Mã nhân viên": employee.employee_id,
                "Họ tên": employee.full_name,
                "Phòng ban": employee.department,
                "Chức vụ": employee.position,
                "Ngày công chuẩn": report["normal_days"],
                "Ngày đi muộn": report["late_days"],
                "Ngày nửa công": report["half_days"],
                "Tổng ngày có mặt": report["total_attendance_days"],
                "Tổng giờ làm việc": report["total_work_hours"]
            })
        
        elif report_type.startswith('department/'):
            department = report_type.split('/')[1]
            employees = Employee.query.filter_by(department=department, status=True).all()
            if not employees:
                return None, {"error": "No active employees found in this department"}, 404
            
            for employee in employees:
                report = process_employee_attendance(employee.employee_id, start_date, end_date)
                
                data.append({
                    "Mã nhân viên": employee.employee_id,
                    "Họ tên": employee.full_name,
                    "Phòng ban": employee.department,
                    "Chức vụ": employee.position,
                    "Ngày công chuẩn": report["normal_days"],
                    "Ngày đi muộn": report["late_days"],
                    "Ngày nửa công": report["half_days"],
                    "Tổng ngày có mặt": report["total_attendance_days"],
                    "Tổng giờ làm việc": report["total_work_hours"]
                })
        
        elif report_type == 'company':
            employees = Employee.query.filter_by(status=True).all()
            if not employees:
                return None, {"error": "No active employees found"}, 404
            
            for employee in employees:
                report = process_employee_attendance(employee.employee_id, start_date, end_date)
                
                data.append({
                    "Mã nhân viên": employee.employee_id,
                    "Họ tên": employee.full_name,
                    "Phòng ban": employee.department,
                    "Chức vụ": employee.position,
                    "Ngày công chuẩn": report["normal_days"],
                    "Ngày đi muộn": report["late_days"],
                    "Ngày nửa công": report["half_days"],
                    "Tổng ngày có mặt": report["total_attendance_days"],
                    "Tổng giờ làm việc": report["total_work_hours"]
                })
        
        else:
            return None, {"error": "Invalid report type. Use 'employee/<employee_id>', 'department/<department>', or 'company'"}, 400
        
        # Tạo file Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Báo cáo chấm công"
        
        # Thêm tiêu đề
        title_row = [f"BÁO CÁO CHẤM CÔNG - {format_datetime_vn(start_date)} đến {format_datetime_vn(end_date)}"]
        ws.append(title_row)
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=9)
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = Alignment(horizontal="center")
        
        # Thêm hàng trống
        ws.append([])
        
        # Headers
        headers = ["Mã nhân viên", "Họ tên", "Phòng ban", "Chức vụ", "Ngày công chuẩn", "Ngày đi muộn", "Ngày nửa công", "Tổng ngày có mặt", "Tổng giờ làm việc"]
        ws.append(headers)
        
        # Style headers
        for cell in ws[3]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")
        
        # Thêm dữ liệu
        for row_data in data:
            ws.append([
                row_data["Mã nhân viên"],
                row_data["Họ tên"],
                row_data["Phòng ban"],
                row_data["Chức vụ"],
                row_data["Ngày công chuẩn"],
                row_data["Ngày đi muộn"],
                row_data["Ngày nửa công"],
                row_data["Tổng ngày có mặt"],
                row_data["Tổng giờ làm việc"]
            ])
        
        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Giới hạn width tối đa
            ws.column_dimensions[column].width = adjusted_width
        
        # Tạo filename và save
        timestamp = get_vn_datetime().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{report_type.replace('/', '_')}_{timestamp}.xlsx"
        filepath = os.path.join(get_export_path(), filename)
        wb.save(filepath)
        
        return {"message": "Report exported successfully", "download_url": f"/Exports/{filename}", "filename": filename}, None, None
    
    except Exception as e:
        return None, {"error": f"Export failed: {str(e)}"}, 500