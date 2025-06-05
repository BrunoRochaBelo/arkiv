from flask import Blueprint


tag_bp = Blueprint('tag', __name__)

from . import routes  # noqa: E402,F401
