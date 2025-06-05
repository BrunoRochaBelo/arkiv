from flask import Blueprint

folder_bp = Blueprint('folder', __name__)

from . import routes  # noqa
