"""
WSGI entry point for production deployment (Render, Heroku, etc.)

Use with: gunicorn wsgi:app
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try importing from backend (new structure)
    from backend.app import create_app
    app = create_app()
except ImportError as e:
    print(f"Import error from backend: {e}")
    # Fallback to root app.py
    try:
        from app import app
    except ImportError as e2:
        print(f"Import error from root app: {e2}")
        raise

# For production servers
if __name__ == '__main__':
    app.run()
