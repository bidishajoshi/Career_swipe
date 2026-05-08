"""Routes package - API endpoints"""

from flask import Blueprint

# Create blueprints for different route groups
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
job_bp = Blueprint('job', __name__, url_prefix='/api/jobs')
application_bp = Blueprint('application', __name__, url_prefix='/api/applications')

# Import route handlers
from .auth_routes import *
from .job_routes import *
from .application_routes import *

__all__ = ['auth_bp', 'job_bp', 'application_bp']
