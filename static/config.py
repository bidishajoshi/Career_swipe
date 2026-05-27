import os

class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "secret-key")

    # -----------------------------
    # PostgreSQL Database Config
    # -----------------------------
    database_url = os.environ.get("DATABASE_URL")

    # Fix old postgres:// issue
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------
    # Upload Folder
    # -----------------------------
    UPLOAD_FOLDER = "static/uploads"

    # -----------------------------
    # Mail Config (optional)
    # -----------------------------
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")