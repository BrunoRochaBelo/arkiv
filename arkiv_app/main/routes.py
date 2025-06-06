from flask import render_template
from flask_login import current_user

from ..extensions import db
from ..models import Asset, Library
from ..utils import current_org_id
from . import main_bp


@main_bp.route('/')
def index():
    org_id = current_org_id()
    stats = {
        'libs_count': 0,
        'total_images': 0,
        'used_storage': 0,
        'quota': None,
        'plan': None,
        'last_uploads': [],
    }
    if current_user.is_authenticated and org_id:
        stats['libs_count'] = Library.query.filter_by(org_id=org_id).count()
        stats['total_images'] = (
            db.session.query(db.func.count(Asset.id))
            .join(Library)
            .filter(Library.org_id == org_id)
            .scalar()
            or 0
        )
        stats['used_storage'] = (
            db.session.query(db.func.sum(Asset.size))
            .join(Library)
            .filter(Library.org_id == org_id)
            .scalar()
            or 0
        )
        membership = current_user.memberships[0] if current_user.memberships else None
        if membership:
            stats['plan'] = membership.organization.plan
            stats['quota'] = membership.organization.plan.storage_quota_gb * 1024 * 1024 * 1024
        stats['last_uploads'] = (
            Asset.query
            .join(Library)
            .filter(Library.org_id == org_id)
            .order_by(Asset.created_at.desc())
            .limit(3)
            .all()
        )
    return render_template('home.html', title='Início', stats=stats)
