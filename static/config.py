"""
config.py – CareerSwipe Application Configuration
Supports both local development (SQLite fallback) and production (PostgreSQL on Render).
All sensitive values are loaded from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "careerswipe-dev-secret-2026-CHANGE-ME")

    # ── Database ──────────────────────────────────────────────────────────────
    # Render provides DATABASE_URL starting with "postgres://"; SQLAlchemy
    # requires "postgresql://". The replace() call fixes this automatically.
    # Fallback to local PostgreSQL if DATABASE_URL is not set.
    _raw_db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/careerswipe")
    if _raw_db_url.startswith("postgres://"):
        _raw_db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Connection pool settings – optimized for PostgreSQL
    # Require SSL only for remote databases (like Render)
    _is_remote = "localhost" not in _raw_db_url and "127.0.0.1" not in _raw_db_url

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,       # health-check before each query
        "pool_recycle": 300,         # recycle connections every 5 min
        **({"connect_args": {"sslmode": "require"}} if _is_remote else {}),
    }

    # ── Mail (Gmail SMTP) ─────────────────────────────────────────────────────
    MAIL_SERVER        = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT          = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS       = True
    MAIL_USERNAME      = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD      = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER= os.environ.get("MAIL_USERNAME", "noreply@careerswipe.app")

    # ── File Uploads ──────────────────────────────────────────────────────────
    UPLOAD_FOLDER      = os.path.join("static", "uploads")
    RESUME_FOLDER      = os.path.join(UPLOAD_FOLDER, "resumes")
    LOGO_FOLDER        = os.path.join(UPLOAD_FOLDER, "logos")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload size
