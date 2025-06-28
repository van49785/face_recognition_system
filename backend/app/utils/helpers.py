# Tiện ích khác (format ngày giờ, export file...)
import pytz
from datetime import datetime
import os

def format_datetime_vn(dt):
    """Helper function để format datetime sang timezone Việt Nam"""
    if dt is None:
        return None
    
    # Vì model đã lưu naive datetime theo timezone VN, 
    # chỉ cần localize rồi format
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    dt_vn = vn_tz.localize(dt)
    return dt_vn.strftime("%d/%m/%Y %H:%M:%S")

def get_vn_datetime():
    """Helper function để lấy datetime hiện tại theo timezone VN (naive)"""
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    return datetime.now(vn_tz).replace(tzinfo=None)


def format_time_vn(dt):
    """Helper function để format time sang string"""
    if dt is None:
        return None
    return dt.strftime("%H:%M:%S")


def get_upload_path():
    """Tạo đường dẫn upload nhất quán"""
    # Lấy thư mục app/ (từ app/routes/ lên 1 cấp)
    # __file__ = app/routes/employee.py
    # dirname(__file__) = app/routes/
    # dirname(dirname(__file__)) = app/
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(app_dir, "data", "uploads")