from flask import Flask
from .config import config_by_name
from .extensions import init_extensions, db
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    dsn = app.config.get('SENTRY_DSN')
    if dsn:
        sentry_sdk.init(dsn=dsn, integrations=[FlaskIntegration()])

    init_extensions(app)

    from .main.routes import main_bp
    from .api import api_bp
    from .auth import auth_bp
    from .library import library_bp
    from .folder import folder_bp
    from .asset import asset_bp
    from .tag import tag_bp
    from .search import search_bp
    from .reports import reports_bp
    from .admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(folder_bp)
    app.register_blueprint(asset_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)

    # Só criar tabelas se estiver em desenvolvimento
    if config_name == 'development':
        with app.app_context():
            db.create_all()

    return app
