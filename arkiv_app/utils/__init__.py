from flask_login import current_user


def current_org_id():
    """Return the org_id of the current user's first membership, if any."""
    if current_user.is_authenticated and current_user.memberships:
        return current_user.memberships[0].org_id
    return None
