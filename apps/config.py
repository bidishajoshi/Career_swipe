"""
app/config.py – CareerSwipe Application Configuration
All sensitive values are loaded from environment variables via .env.
PostgreSQL is required – no SQLite fallback in production.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _is_postgres(url: str) -> bool:
    """Return True if the URL points to a PostgreSQL database."""
    return url.startswith('postgresql://') or url.startswith('postgres://')


class Config:
    # ── Security ───────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'careerswipe-dev-secret-CHANGE-IN-PROD')

    # ── Database ───────────────────────────────────────────────────────────────
    # Render provides DATABASE_URL starting with "postgres://"; SQLAlchemy
    # requires "postgresql://". The replace() call fixes this automatically.
<<<<<<< HEAD
    _raw = os.environ.get('DATABASE_URL', 'sqlite:///careerswipe.db')
=======
    # Falls back to local sqlite in dev/testing context if DATABASE_URL is not set.
    _raw = os.environ.get('DATABASE_URL', '')
>>>>>>> 1b6a9d6fb4d8c291861c93d80aeb6cc4707b54c9
    if _raw.startswith('postgres://'):
        _raw = _raw.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = _raw
    SQLALCHEMY_TRACK_MODIFICATIONS = False

<<<<<<< HEAD
    # Connection pool — sslmode only applies to PostgreSQL, not SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,   # health-check before each query
        'pool_recycle': 300,     # recycle connections every 5 min
        **({'connect_args': {'sslmode': 'require'}} if _is_postgres(_raw) else {}),
=======
    # Check database driver and target server to conditionally apply SSL settings
    _is_sqlite = _raw.startswith('sqlite')
    _is_postgres = _raw.startswith('postgresql')
    _is_remote = _is_postgres and 'localhost' not in _raw and '127.0.0.1' not in _raw

    # Connection pool – safe for long-running PostgreSQL connections
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,       # health-check before each query
        'pool_recycle': 300,         # recycle connections every 5 min
>>>>>>> 1b6a9d6fb4d8c291861c93d80aeb6cc4707b54c9
    }

    if not _is_sqlite and _raw:
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {
            'sslmode': 'require' if _is_remote else 'prefer'
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
    """Local development – relaxes SSL for SQLite."""
    DEBUG = True
<<<<<<< HEAD
=======
    
    # Enable SQLite fallback if DATABASE_URL is not set or empty
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///careerswipe.db')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = _db_url

    _is_sqlite = _db_url.startswith('sqlite')
    _is_postgres = _db_url.startswith('postgresql')
    _is_remote = _is_postgres and 'localhost' not in _db_url and '127.0.0.1' not in _db_url

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    if not _is_sqlite and _db_url:
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {
            'sslmode': 'require' if _is_remote else 'prefer'
        }
>>>>>>> 1b6a9d6fb4d8c291861c93d80aeb6cc4707b54c9


class ProductionConfig(Config):
    """Production on Render – strict SSL enforced via Config base class."""
    DEBUG = False
