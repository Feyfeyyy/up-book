import secrets

from app.environment import API_KEY, DATABASE_URI, SECRET_KEY


class Config(object):
    DEBUG = False
    TESTING = False
    API_KEY = API_KEY
    SECRET_KEY = SECRET_KEY
    DATABASE_URI = DATABASE_URI
    ALLOWED_EXTENSIONS = ["CSV"]
    UPLOAD_FOLDER = "app/static/uploads"
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
