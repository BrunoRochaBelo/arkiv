from flask import Flask
from .config import config_by_name
from .extensions import init_extensions



def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    init_extensions(app)

    from .main.routes import main_bp
    from .api import api_bp
    from .auth import auth_bp
    from .library import library_bp
    from .folder import folder_bp
    from .asset import asset_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(folder_bp)
    app.register_blueprint(asset_bp)

    return app
