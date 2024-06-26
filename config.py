import secrets
from pathlib import Path

from app.environment import (
    AWS_API_KEY,
    AWS_BUCKET_NAME,
    AWS_SECRET_KEY,
    DATABASE_URI,
    ENV_KEY,
)

RELATIVE_UPLOAD_FOLDER = Path("app/static/uploads")


class Config(object):
    ENV = ENV_KEY
    DEBUG = False
    TESTING = False
    AWS_BUCKET_NAME = AWS_BUCKET_NAME
    AWS_API_KEY = AWS_API_KEY
    AWS_SECRET_KEY = AWS_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = ["CSV"]
    UPLOAD_FOLDER = Path(__file__).resolve().parent / RELATIVE_UPLOAD_FOLDER
    SESSION_COOKIE_SECURE = True
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    SECRET_KEY = secrets.token_urlsafe(16)


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = False
    SESSION_PERMANENT = True
