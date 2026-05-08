"""
WSGI entry point for production deployment (Render, Heroku, etc.)

Use with: gunicorn wsgi:app
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the app factory
from backend.app import create_app, app

# For production servers
if __name__ == '__main__':
    app.run()
