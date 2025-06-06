from flask import Flask
from .config import config_by_name
from .extensions import init_extensions, db, csrf
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_login import current_user

from .utils import current_org_id
from .utils.audit import ensure_audit_log_schema
from .auth.routes import oauth

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    dsn = app.config.get('SENTRY_DSN')
    if dsn:
        sentry_sdk.init(dsn=dsn, integrations=[FlaskIntegration()])

        @app.before_request
        def _sentry_context():
            if current_user.is_authenticated:
                with sentry_sdk.configure_scope() as scope:
                    scope.set_user({'id': current_user.id, 'email': current_user.email})
                    # set organization tag only if available
                    org_id = current_org_id()
                    if org_id is not None:
                        scope.set_tag('org_id', org_id)

    init_extensions(app)
    if oauth:
        oauth.init_app(app)

    from .main.routes import main_bp
    from .api import api_bp
    from .auth import auth_bp
    from .library import library_bp
    from .folder import folder_bp
    from .asset import asset_bp
    from .tag import tag_bp
    from .search import search_bp
    from .dashboard import dashboard_bp
    from .reports import reports_bp
    from .admin import admin_bp
    from .organization import organization_bp
    from .trash import trash_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(folder_bp)
    app.register_blueprint(asset_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(organization_bp)
    app.register_blueprint(trash_bp)
    csrf.exempt(api_bp)

    @app.after_request
    def _security_headers(resp):
        resp.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' https:;"
        resp.headers['X-Frame-Options'] = 'DENY'
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        resp.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
        return resp

    # Só criar tabelas e dados iniciais em desenvolvimento/produção
    if config_name != 'testing':
        with app.app_context():
            db.create_all()
            ensure_audit_log_schema()
            from .utils.create_initial_data import ensure_initial_data
            ensure_initial_data()
    else:
        with app.app_context():
            ensure_audit_log_schema()

    return app
