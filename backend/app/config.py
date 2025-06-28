import os

class Config:

    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///attendance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_FAILED_ATTEMPTS = 5
    LOCK_DURATION_MINUTES = 30
    SESSION_DURATION_HOURS = 2
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'  # Dạng: Bearer <token>


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'