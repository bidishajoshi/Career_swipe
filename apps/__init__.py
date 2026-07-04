"""
app/__init__.py – CareerSwipe Application Factory
Creates and configures the Flask app instance.
"""

import os
from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

# CSRF protection via Flask-WTF
try:
    from flask_wtf import CSRFProtect
    csrf = CSRFProtect()
except ImportError:
    csrf = None

from .extensions import db, migrate, mail
from .config import Config
from .services import EligibilityService

# Blueprint imports moved to module level for clarity
from .routes.auth import auth_bp
from .routes.seeker import seeker_bp
from .routes.company import company_bp
from .routes.jobs import jobs_bp
from .routes.notifications import notifications_bp
from .routes.profile import profile_bp


def create_app(config_class=Config):
    """Application factory pattern – creates a fully configured Flask app."""
    app = Flask(
        __name__,
        # Templates and static files live one level up (project root)
        template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
    )
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    if csrf:
        csrf.init_app(app)  # Enable CSRF protection for all forms

    @app.context_processor
    def inject_csrf_fallback():
        """Ensure templates don't crash if CSRF is disabled or fails to load."""
        if 'csrf_token' not in app.jinja_env.globals:
            return {'csrf_token': lambda: ""}
        return {}

    # Ensure upload directories exist
    with app.app_context():
        os.makedirs(app.config['RESUME_FOLDER'], exist_ok=True)
        os.makedirs(app.config['LOGO_FOLDER'], exist_ok=True)
        db.create_all()
        try:
            EligibilityService.create_eligibility_questions()
        except Exception:
            app.logger.debug('Default eligibility question initialization skipped.', exc_info=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(seeker_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(profile_bp)

    if csrf:
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api/'):
                view_func = app.view_functions.get(rule.endpoint)
                if view_func:
                    csrf.exempt(view_func)

    @app.route("/api/health")
    def health_check():
        return {"status": "healthy", "service": "CareerSwipe"}, 200

    # Legacy templates still reference the original monolithic app endpoint names.
    # These aliases keep url_for(...) working while the blueprint routes handle requests.
    legacy_endpoints = {
        'index': '/',
        'upload_resume_step': '/upload-resume',
        'register_seeker': '/register/seeker',
        'register_company': '/register/company',
        'login_seeker': '/login/seeker',
        'login_company': '/login/company',
        'logout': '/logout',
        'seeker_dashboard': '/dashboard/seeker',
        'edit_seeker_profile': '/profile/seeker',
        'company_dashboard': '/dashboard/company',
        'company_insights': '/company/insights',
        'post_job': '/jobs/post',
        'notifications_history': '/notifications',
    }
    for endpoint, rule in legacy_endpoints.items():
        if endpoint not in app.view_functions:
            app.add_url_rule(rule, endpoint=endpoint, redirect_to=rule)
            
    # Add rules with path variables
    if 'update_applicant' not in app.view_functions:
        app.add_url_rule(
            '/applicant/<int:swipe_id>/<action>',
            endpoint='update_applicant',
            redirect_to='/applicant/%(swipe_id)s/%(action)s',
        )
    if 'job_applicants' not in app.view_functions:
        app.add_url_rule(
            '/company/job/<int:job_id>/applicants',
            endpoint='job_applicants',
            redirect_to='/company/job/%(job_id)s/applicants',
        )

    # Global error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        app.logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
        return render_template('error.html', error=str(e)), 500

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', error='Page not found (404)'), 404

    # Register custom Jinja filters
    from utils.helpers import format_job_location
    app.jinja_env.filters['format_location'] = format_job_location
    return app
