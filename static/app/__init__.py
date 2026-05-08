"""
app/__init__.py – CareerSwipe Application Factory
Creates and configures the Flask app instance.
"""

import os
from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from .extensions import db, migrate, mail
from .config import Config


def create_app(config_class=Config):
    """Application factory pattern – creates a fully configured Flask app."""
    app = Flask(
        __name__,
        # Templates and static files live one level up (project root)
        template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
    )
    app.config.from_object(config_class)

    # ── Initialize extensions ──────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # ── Ensure upload directories exist ───────────────────────────────────────
    with app.app_context():
        os.makedirs(app.config['RESUME_FOLDER'], exist_ok=True)
        os.makedirs(app.config['LOGO_FOLDER'], exist_ok=True)

    # ── Register blueprints ────────────────────────────────────────────────────
    from .routes.auth import auth_bp
    from .routes.seeker import seeker_bp
    from .routes.company import company_bp
    from .routes.jobs import jobs_bp
    from .routes.notifications import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(seeker_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(notifications_bp)

    # ── Global error handlers ──────────────────────────────────────────────────
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        import traceback
        traceback.print_exc()
        return render_template('error.html', error=str(e)), 500

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', error='Page not found (404)'), 404

    return app
