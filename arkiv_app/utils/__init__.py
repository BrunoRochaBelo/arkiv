from functools import wraps
from flask import abort
from flask_login import current_user
from ..extensions import login_manager


def current_org_id():
    """Return the org_id of the current user's first membership, if any."""
    if current_user.is_authenticated and current_user.memberships:
        return current_user.memberships[0].org_id
    return None


def role_required(*roles):
    """Ensure the current user has one of the given roles.

    Usage::

        @role_required("OWNER", "MANAGER")
        def view():
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            membership = current_user.memberships[0] if current_user.memberships else None
            if not membership or membership.role not in roles:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
