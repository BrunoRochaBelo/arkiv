from flask import Blueprint\n\nreports_bp = Blueprint('reports', __name__)\n\nfrom . import routes  # noqa: E402,F401
