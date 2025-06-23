from flask import Flask
from flask_cors import CORS
from .config import Config
from dotenv import load_dotenv
from .db import db, migrate  
from .routes.attendance_routes import attendance_bp
from .routes.employee_route import employee_bp
import os

load_dotenv()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register routes sau khi init extensions
    app.register_blueprint(attendance_bp)
    app.register_blueprint(employee_bp)

    from . import models  # đảm bảo model được import sau khi db đã sẵn sàng

    return app
