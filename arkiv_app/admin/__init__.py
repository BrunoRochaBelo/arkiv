from flask import Blueprint\n\nadmin_bp = Blueprint('admin', __name__, url_prefix='/admin')\n\nfrom . import routes  # noqa: E402,F401
