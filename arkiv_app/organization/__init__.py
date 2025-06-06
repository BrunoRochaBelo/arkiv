from flask import Blueprint

organization_bp = Blueprint('organization', __name__, url_prefix='/org')

from . import routes  # noqa: E402,F401
