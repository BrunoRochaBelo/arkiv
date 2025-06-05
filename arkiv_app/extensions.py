from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
from pythonjsonlogger import jsonlogger
import logging
from flask_mail import Mail
from flask_login import LoginManager

# Instances of extensions

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
metrics = PrometheusMetrics()

def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    metrics.init_app(app)
    _setup_logging(app)
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

def _setup_logging(app):
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(formatter)
    app.logger.setLevel(app.config.get('LOG_LEVEL', 'INFO'))
    if not app.logger.handlers:
        app.logger.addHandler(handler)
