from datetime import datetime, timedelta
from typing import Tuple, Optional, Union
import pytz
import uuid 

from app.db import db
from app.models.admin import Admin
from app.models.employee import Employee 
from app.models.audit_log import AuditLog
from app.models.session import Session
from app.utils.security import generate_jwt_token
from app.config import Config 

VN_TIMEZONE = pytz.timezone("Asia/Ho_Chi_Minh")

# Hàm hỗ trợ khóa tài khoản chung cho cả Admin và Employee
def _lock_account(user_obj: Union[Admin, Employee], duration_minutes: int) -> None:
    """Khóa tài khoản của Admin hoặc Employee trong thời gian nhất định."""
    user_obj.locked_until = datetime.now(VN_TIMEZONE).replace(tzinfo=None) + timedelta(minutes=duration_minutes)
    user_obj.failed_attempts = 0 # Reset failed attempts khi khóa
    db.session.commit()
    # Có thể thêm AuditLog ở đây nếu muốn log việc khóa tài khoản

def login_admin(
        username: str,
        password: str,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Đăng nhập Admin.
    Returns:
        token (str | None), error (str | None)
    """
    admin: Admin | None = Admin.query.filter_by(username=username).first()
    if not admin: 
        return None, "Invalid username or password"
    
    now_vn = datetime.now(VN_TIMEZONE).replace(tzinfo=None)
    if admin.locked_until and admin.locked_until > now_vn:
        AuditLog.log_login(
            admin_id=admin.id,
            success=False,
        )
        return None, "Account is locked. Please try again later."
    
    if not admin.check_password(password):
        admin.failed_attempts += 1
        status_msg = "Invalid username or password."

        if admin.failed_attempts >= Config.MAX_LOGIN_ATTEMPTS:
            _lock_account(admin, Config.LOCK_DURATION_MINUTES) # SỬ DỤNG HÀM CHUNG
            status_msg = (
                f"Too many failed login attempts {Config.MAX_LOGIN_ATTEMPTS} times, Your account has been locked for {Config.LOCK_DURATION_MINUTES} minutes."
            )

        db.session.commit()
        AuditLog.log_login(
            admin_id=admin.id,
            success=False,
        )
        return None, status_msg
    
    # Đăng nhập thành công, reset
    admin.failed_attempts = 0
    admin.locked_until = None
    admin.last_login = now_vn # Cập nhật last_login

    Session.query.filter_by(admin_id=admin.id, is_valid=True).update({'is_valid': False})
    db.session.commit()

    # Tạo JWT token
    token = generate_jwt_token({'user_id': admin.id, 'role': 'admin'}) # Payload cho Admin

    # Ghi session (SỬ DỤNG PHƯƠNG THỨC create_session MỚI)
    session = Session.create_session(
        admin_id=admin.id,
        jwt_token=token,
        is_admin_session=True,
    )

    # Ghi log
    AuditLog.log_login(
        admin_id=admin.id,
        success=True,
    )

    return token, None

def login_employee(employee_id_or_email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Đăng nhập Nhân viên. Có thể dùng employee_id hoặc email làm username.
    Returns:
        token (str | None), error (str | None)
    """
    employee: Employee | None = Employee.query.filter(
        (Employee.employee_id == employee_id_or_email.upper()) | (Employee.email == employee_id_or_email)
    ).first()

    # Kiểm tra nếu không tìm thấy nhân viên hoặc nhân viên chưa có tài khoản đăng nhập
    if not employee or not employee.username: 
        return None, "Invalid username or password."

    now_vn = datetime.now(VN_TIMEZONE).replace(tzinfo=None)
    if employee.locked_until and employee.locked_until > now_vn:
        # Có thể thêm AuditLog cho employee login nếu có AuditLog model cho employee
        return None, "Account is locked. Please try again later."

    # Kiểm tra mật khẩu
    if not employee.check_password(password):
        employee.failed_attempts += 1
        status_msg = "Invalid username or password."

        if employee.failed_attempts >= Config.MAX_LOGIN_ATTEMPTS:
            _lock_account(employee, Config.LOCK_DURATION_MINUTES) # SỬ DỤNG HÀM CHUNG
            status_msg = (
                f"Too many failed login attempts  {Config.MAX_LOGIN_ATTEMPTS} times, your account has been locked for {Config.LOCK_DURATION_MINUTES} minutes."
            )
        db.session.commit()
        # Có thể thêm AuditLog cho employee login failed
        return None, status_msg

    # Đăng nhập thành công, reset
    employee.failed_attempts = 0
    employee.locked_until = None
    employee.last_login = now_vn # Cập nhật last_login
    db.session.commit()

    # Tạo JWT token cho nhân viên. Payload chứa employee_id và role.
    token = generate_jwt_token({'employee_id': employee.employee_id, 'role': 'employee', 'user_id': employee.id}) 

    # Ghi session cho nhân viên (SỬ DỤNG PHƯƠNG THỨC create_session MỚI)
    # Vô hiệu hóa các session cũ của nhân viên này để chỉ có 1 session active
    Session.query.filter_by(employee_id=employee.id, is_valid=True).update({'is_valid': False})
    db.session.commit()

    Session.create_session(
        employee_id=employee.id,
        jwt_token=token,
        is_admin_session=False,
    )
    # Có thể thêm AuditLog cho employee login success

    return token, None

def set_employee_password(employee_id: str, new_password: str, username: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Thiết lập mật khẩu và username cho nhân viên.
    Nếu username không được cung cấp, sẽ mặc định là employee_id.
    """
    employee = Employee.query.filter_by(employee_id=employee_id.upper()).first()
    if not employee:
        return False, "Employe not found."
    
    if not new_password or len(new_password) < Config.MIN_PASSWORD_LENGTH:
        return False, f"Password must have at least {Config.MIN_PASSWORD_LENGTH} characters."

    # Kiểm tra username nếu được cung cấp
    if username:
        # Nếu username được cung cấp và khác với employee_id/email hiện tại, kiểm tra tính duy nhất
        if username != employee.employee_id and username != employee.email:
            existing_employee_with_username = Employee.query.filter(
                (Employee.employee_id == username.upper()) | (Employee.email == username)
            ).first()
            if existing_employee_with_username and existing_employee_with_username.id != employee.id:
                return False, "Username already exists for another employee. Please select a different username."
        employee.username = username # Đặt username theo yêu cầu
    else:
        employee.username = employee.employee_id # Mặc định username là employee_id

    employee.set_password(new_password)
    employee.updated_at = datetime.now(VN_TIMEZONE).replace(tzinfo=None)
    db.session.commit()
    return True, None

# CẬP NHẬT: Hàm logout chung
def logout_user(user_jwt_token: str) -> None:
    """Vô hiệu hóa session của người dùng (Admin hoặc Employee)"""
    Session.invalidate_token_hash(user_jwt_token)
    # Có thể thêm AuditLog ở đây, cần biết user_id và role từ token

# CẬP NHẬT: Hàm verify token chung
def verify_token(jwt_payload: dict) -> Optional[Union[Admin, Employee]]:
    """
    Trả về đối tượng Admin hoặc Employee nếu token hợp lệ & session vẫn active.
    """
    user_id = jwt_payload.get("user_id")
    role = jwt_payload.get("role")
    employee_id_from_payload = jwt_payload.get("employee_id") 

    if user_id is None or role is None:
        return None
    
    user_obj = None
    if role == 'admin':
        user_obj = Admin.query.get(user_id)
    elif role == 'employee':
        # Tìm employee bằng id từ payload (là id của bảng employees)
        user_obj = Employee.query.get(user_id)
        # Hoặc có thể dùng employee_id nếu bạn lưu employee_id trong payload và muốn tìm theo đó
        # user_obj = Employee.query.filter_by(employee_id=employee_id_from_payload).first()
    
    if not user_obj:
        return None
    
    hashed = Session.hash_token(jwt_payload["jti"]) if "jti" in jwt_payload else None
    if hashed:
        # Tìm session dựa trên user_id và loại session
        session_query = Session.query.filter_by(jwt_token_hash=hashed, is_valid=True)
        if role == 'admin':
            session_query = session_query.filter_by(admin_id=user_id, is_admin_session=True)
        elif role == 'employee':
            session_query = session_query.filter_by(employee_id=user_id, is_admin_session=False)

        session = session_query.first()

        if session and not session.is_expired():
            session.update_activity() # Cập nhật thời gian hoạt động cuối
            return user_obj
        
    return None