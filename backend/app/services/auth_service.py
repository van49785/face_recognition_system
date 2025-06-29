from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional

from app.db import db
from app.models.admin import Admin
from app.models.audit_log import AuditLog
from app.models.session import Session
from app.utils.security import check_password_hash, generate_jwt_token
from app.config import *
import pytz

def _lock_account(admin: Admin) -> None:
    admin.locked_until = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None) + timedelta(minutes=Config.LOCK_DURATION_MINUTES)
    db.session.commit()

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
        return None, "Invalid account"
    
    now_utc = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
    if admin.locked_until and admin.locked_until > now_utc:
        AuditLog.log_login(
            admin_id=admin.id,
            success=False,
        )
        return None, "Account is locked. Please try again later"
    
    if not check_password_hash(admin.password_hash, password):
        admin.failed_attempts += 1
        status_msg = "Wrong password"

        if admin.failed_attempts >= Config.MAX_FAILED_ATTEMPTS:
            _lock_account(admin)
            status_msg = (
                f"Wrong password more than {Config.MAX_FAILED_ATTEMPTS} times, account is locked for {Config.LOCK_DURATION_MINUTES} minutes"
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
    db.session.commit()

    # Tạo JWT token
    token = generate_jwt_token(admin.id)

    # Ghi session
    Session.create_session(
        admin_id=admin.id,
        jwt_token=token,
    )

    # Ghi log
    AuditLog.log_login(
        admin_id=admin.id,
        success=True,
    )

    return token, None

def logout_admin(
        admin_id: int,
        jwt_token: str,
) -> None:
    Session.invalidate_token_hash(jwt_token)

    AuditLog.log_action(
        admin_id=admin_id,
        action="logout",
        details="User logout",
        status="success",
    )

def verify_admin_token(jwt_payload: dict) -> Optional[Admin]:
    """
    Trả về đối tượng Admin nếu token hợp lệ & session vẫn active.
    """
    admin_id = jwt_payload.get("sub")
    if admin_id is None:
        return None
    
    admin = Admin.query.get(admin_id)
    if not admin:
        return None
    
    hashed = Session.hash_token(jwt_payload["jti"]) if "jti" in jwt_payload else None
    if hashed:
        session = Session.query.filter_by(
            admin_id=admin_id, jwt_token_hash=hashed, is_valid=True
        ).first()
        if session and not session.is_expired():
            session.update_activity()
            return admin
        
    return None
