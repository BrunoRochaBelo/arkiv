from flask import Blueprint

ticket_bp = Blueprint('ticket', __name__)

from . import routes  # noqa
