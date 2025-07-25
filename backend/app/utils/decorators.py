# Các hằng số dùng chung
# app/utils/decorators.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required # Import jwt_required
from app.models.admin import Admin # Đảm bảo đường dẫn import Admin đúng

def admin_required(fn):
    """
    Decorator to ensure that only authenticated administrators can access the route.
    It implicitly requires a valid JWT token.
    """
    @wraps(fn)
    @jwt_required() # Đảm bảo JWT token được yêu cầu trước khi kiểm tra admin
    def wrapper(*args, **kwargs):
        admin_id = get_jwt_identity() # Lấy ID từ JWT token
        if not admin_id:
            return jsonify({"error": "Admin identity not found in token"}), 401

        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({"error": "Admin not found"}), 404
        
        # Thêm logic kiểm tra vai trò nếu bạn có cột 'role' trong bảng Admin
        # Ví dụ: if admin.role not in ['admin', 'super_admin']:
        #     return jsonify({"error": "Admin privilege required"}), 403
        
        return fn(*args, **kwargs)
    return wrapper