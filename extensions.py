from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from utils.mail_helper import Mail

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
