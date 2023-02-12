import secrets


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "secret"
    DATABASE_URI = "sqlite:///database.db"
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
    DATABASE_URI = "sqlite:///database.db"
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = True


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True
    TESTING = True
    DATABASE_URI = "sqlite:///database.db"
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = True
