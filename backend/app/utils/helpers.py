# backend/app/utils/helpers.py

# Tiện ích khác (format ngày giờ, export file...)
import pytz
from datetime import datetime
import os
from flask import current_app # Cần import current_app để lấy đường dẫn gốc của ứng dụng

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
    """
    Tạo đường dẫn upload nhất quán.
    Sẽ trỏ đến thư mục 'data/uploads' nằm cùng cấp với thư mục 'app' (trong thư mục 'backend').
    """
    # current_app.root_path là đường dẫn tuyệt đối đến thư mục 'app' (ví dụ: /path/to/your_project/backend/app)
    # Để tới thư mục 'backend', chúng ta đi lên một cấp từ app_root_path
    backend_root = os.path.abspath(os.path.join(current_app.root_path, '..'))
    
    # Sau đó, nối với 'data/uploads' để tạo đường dẫn đích
    upload_dir = os.path.join(backend_root, 'data', 'uploads')
    print(f"DEBUG: Upload path generated by helpers: {upload_dir}") # <-- THÊM DÒNG NÀY
    return upload_dir

