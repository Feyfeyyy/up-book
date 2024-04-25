import secrets
from pathlib import Path

from app.environment import AWS_API_KEY, DATABASE_URI, AWS_SECRET_KEY

RELATIVE_UPLOAD_FOLDER = Path("app/static/uploads")


class Config(object):
    DEBUG = False
    TESTING = False
    AWS_API_KEY = AWS_API_KEY
    AWS_SECRET_KEY = AWS_SECRET_KEY
    DATABASE_URI = DATABASE_URI
    ALLOWED_EXTENSIONS = ["CSV"]
    UPLOAD_FOLDER = Path(__file__).resolve().parent / RELATIVE_UPLOAD_FOLDER
    SESSION_COOKIE_SECURE = True
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    SECRET_KEY = secrets.token_urlsafe(16)


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = True


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = True
