from flask import Flask
from .config import config_by_name
from .extensions import init_extensions, db

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    init_extensions(app)

    from .main.routes import main_bp
    from .api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Só criar tabelas se estiver em desenvolvimento
    if config_name == 'development':
        with app.app_context():
            db.create_all()

    return app
