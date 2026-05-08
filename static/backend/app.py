"""
CareerSwipe Backend - Main Application Entry Point

This is the main Flask application that integrates all backend components.
Supports both local development and Render production deployment.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

# Import extensions
from extensions import db, migrate, mail

# Import configuration
from backend.config import app_config

# Import blueprints (API routes)
from backend.routes import auth_bp, job_bp, application_bp


def create_app(config_class=None):
    """
    Application factory pattern
    Creates and configures the Flask application
    
    Args:
        config_class: Configuration class to use
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        config_class = app_config
    
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Enable CORS for frontend communication
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints (API routes)
    app.register_blueprint(auth_bp)
    app.register_blueprint(job_bp)
    app.register_blueprint(application_bp)
    
    # ── Database Initialization ────────────────────────────────────────────
    with app.app_context():
        try:
            # Create all tables if they don't exist
            # In production, use Flask-Migrate instead
            db.create_all()
            print("✓ Database tables created/verified successfully")
        except Exception as e:
            print(f"⚠ Database initialization note: {e}")
    
    # ── Health Check Endpoint ──────────────────────────────────────────────
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'healthy',
            'service': 'CareerSwipe Backend',
            'version': '1.0.0'
        }), 200
    
    # ── Error Handlers ─────────────────────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors"""
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'error': str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle not found errors"""
        return jsonify({
            'success': False,
            'message': 'Endpoint not found',
            'error': str(error)
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle method not allowed errors"""
        return jsonify({
            'success': False,
            'message': 'Method not allowed',
            'error': str(error)
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle internal server errors"""
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': str(error)
        }), 500
    
    # ── Request/Response Hooks ────────────────────────────────────────────
    @app.after_request
    def after_request(response):
        """Add security headers to all responses"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    """
    Entry point for local development
    
    For production (Render), use: gunicorn wsgi:app
    For local development, use: python backend/app.py
    """
    
    # Get configuration from environment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') == 'True'
    
    print(f"""
    ╔════════════════════════════════════════════════════╗
    ║           CareerSwipe Backend Server               ║
    ╠════════════════════════════════════════════════════╣
    ║ Environment: {os.environ.get('FLASK_ENV', 'development'):40} ║
    ║ Database: {os.environ.get('DATABASE_URL', 'SQLite (Local)')[:40]:40} ║
    ║ Debug Mode: {str(debug):40} ║
    ║ API Base URL: http://localhost:{port}/api             ║
    ║ Health Check: http://localhost:{port}/api/health     ║
    ╚════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
