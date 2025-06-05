from flask import Blueprint

asset_bp = Blueprint('asset', __name__)

from . import routes  # noqa
