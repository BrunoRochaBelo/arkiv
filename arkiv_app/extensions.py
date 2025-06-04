from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# Configurar logger (pode integrar com Sentry ou Loki depois)
logger = logging.getLogger(__name__)