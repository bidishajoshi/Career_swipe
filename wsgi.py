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

# Use the factory pattern to create the Flask app
from apps import create_app

app = create_app()

# For production servers
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
