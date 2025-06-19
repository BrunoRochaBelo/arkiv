from flask import Blueprint

poll_bp = Blueprint('poll', __name__)

from . import routes  # noqa
