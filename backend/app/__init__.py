from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config
from dotenv import load_dotenv
from .routes.attendance_routes import attendance_bp
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register blueprints here
    app.register_blueprint(attendance_bp)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Import models after app context is available
    from . import models  # This will trigger the import of all models
    


    return app