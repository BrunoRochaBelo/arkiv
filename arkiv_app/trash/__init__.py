from flask import Blueprint

trash_bp = Blueprint('trash', __name__, url_prefix='/trash')

from . import routes  # noqa
