from flask import Blueprint

notice_bp = Blueprint('notice', __name__)

from . import routes  # noqa
