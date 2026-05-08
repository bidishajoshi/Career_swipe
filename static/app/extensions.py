"""
app/extensions.py – Shared Flask extension instances.
Import from here everywhere to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail

db      = SQLAlchemy()
migrate = Migrate()
mail    = Mail()
