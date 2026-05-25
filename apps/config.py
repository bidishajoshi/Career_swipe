"""
app/config.py – CareerSwipe Application Configuration
All sensitive values are loaded from environment variables via .env.
PostgreSQL is required – no SQLite fallback in production.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Security ───────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'careerswipe-dev-secret-CHANGE-IN-PROD')

    # ── Database (PostgreSQL only) ─────────────────────────────────────────────
    # Render provides DATABASE_URL starting with "postgres://"; SQLAlchemy
    # requires "postgresql://". The replace() call fixes this automatically.
    _raw = os.environ.get('DATABASE_URL', '')
    if _raw.startswith('postgres://'):
        _raw = _raw.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = _raw
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Connection pool – safe for long-running PostgreSQL connections
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,       # health-check before each query
        'pool_recycle': 300,         # recycle connections every 5 min
        'connect_args': {'sslmode': 'require'},
    }

    # ── Mail (Gmail SMTP) ──────────────────────────────────────────────────────
    MAIL_SERVER         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS        = True
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', 'noreply@careerswipe.app')

    # ── File Uploads ───────────────────────────────────────────────────────────
    UPLOAD_FOLDER       = os.path.join('static', 'uploads')
    RESUME_FOLDER       = os.path.join(UPLOAD_FOLDER, 'resumes')
    LOGO_FOLDER         = os.path.join(UPLOAD_FOLDER, 'logos')
    MAX_CONTENT_LENGTH  = 10 * 1024 * 1024  # 10 MB max upload size


class DevelopmentConfig(Config):
    """Local development – may relax SSL if needed."""
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        # Only require SSL if DATABASE_URL is set (remote dev DB)
        **(
            {'connect_args': {'sslmode': 'require'}}
            if os.environ.get('DATABASE_URL') else {}
        ),
    }


class ProductionConfig(Config):
    """Production on Render – strict SSL enforced."""
    DEBUG = False
