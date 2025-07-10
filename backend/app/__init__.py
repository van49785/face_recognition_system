# backend/app/__init__.py

from flask import Flask # Đảm bảo KHÔNG import send_from_directory ở đây
from flask_cors import CORS 
from .config import Config
from dotenv import load_dotenv
from .db import db, migrate  
from .routes.attendance_routes import attendance_bp
from .routes.employee_route import employee_bp
from .routes.auth_routes import auth_bp
from flask_jwt_extended import JWTManager
import os

load_dotenv()

def create_app(config_class=Config):
    # Lấy đường dẫn gốc của thư mục 'app'
    app_root_path = os.path.dirname(os.path.abspath(__file__))
    
    # Định nghĩa đường dẫn tuyệt đối đến thư mục 'static' mặc định
    default_static_folder = os.path.join(app_root_path, '..', 'static')

    app = Flask(__name__, 
                static_folder=default_static_folder, 
                static_url_path='/static',
            )
    app.config.from_object(config_class)

    jwt = JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)
    
    # Cấu hình CORS chi tiết hơn
    CORS(app, resources={
        r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:5173"], "methods": ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS"]},
        r"/uploads/*": {"origins": ["http://localhost:3000", "http://localhost:5173"], "methods": ["GET", "HEAD", "OPTIONS"]} # Thêm dòng này để CORS cho ảnh
    })

    # Đăng ký blueprints
    app.register_blueprint(attendance_bp)
    app.register_blueprint(employee_bp) # employee_bp đã chứa route /uploads/<path:filename>
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from . import models  

    return app

