"""Backend configuration - Database and application settings"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # ── Application ────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "careerswipe-dev-secret-2026")
    DEBUG = os.environ.get("DEBUG", "False") == "True"
    
    # ── Database ───────────────────────────────────────────────────────────
    # For Render: Use DATABASE_URL environment variable (PostgreSQL)
    # For Local Development: Uses PostgreSQL or falls back to SQLite
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if DATABASE_URL:
        # Render provides DATABASE_URL starting with postgres://
        # SQLAlchemy 1.4+ requires postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or "sqlite:///careerswipe.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Production-safe connection settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,                   # Verify connections before using
        "pool_recycle": 300,                     # Recycle connections after 5 minutes
        "echo": False,                           # Set to True for SQL logging
        "connect_args": {
            "sslmode": "require" if SQLALCHEMY_DATABASE_URI.startswith("postgresql://") and "render.com" in SQLALCHEMY_DATABASE_URI
            else "prefer"
        } if not SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}
    }
    
    # ── Mail ───────────────────────────────────────────────────────────────
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "noreply@careerswipe.app")
    
    # ── File Uploads ───────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join("static", "uploads")
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
    LOGO_FOLDER = os.path.join(UPLOAD_FOLDER, "logos")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload
    
    # ── API Configuration ──────────────────────────────────────────────────
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration (Render)"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Select config based on environment
config_name = os.getenv("FLASK_ENV", "development")
if config_name == "production":
    app_config = ProductionConfig
elif config_name == "testing":
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig
