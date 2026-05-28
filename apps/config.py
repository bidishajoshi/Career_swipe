"""
apps/config.py - CareerSwipe application configuration.
Loads sensitive values from environment variables and supports local SQLite.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "careerswipe-dev-secret-CHANGE-IN-PROD")

    _raw = os.environ.get("DATABASE_URL", "sqlite:///careerswipe.db")
    if _raw.startswith("postgres://"):
        _raw = _raw.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _raw
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _is_sqlite = _raw.startswith("sqlite")
    _is_postgres = _raw.startswith("postgresql")
    _is_remote = _is_postgres and "localhost" not in _raw and "127.0.0.1" not in _raw

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    if not _is_sqlite and _raw:
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {
            "sslmode": "require" if _is_remote else "prefer"
        }

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "noreply@careerswipe.app")

    UPLOAD_FOLDER = os.path.join("static", "uploads")
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
    LOGO_FOLDER = os.path.join(UPLOAD_FOLDER, "logos")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
