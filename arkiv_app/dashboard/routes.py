from datetime import datetime
from flask import render_template
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Asset, Library, Folder, Tag, AuditLog
from ..utils import current_org_id
from . import dashboard_bp


@dashboard_bp.route('/')
@login_required
def overview():
    org_id = current_org_id()
    stats = {
        'assets': 0,
        'storage': 0,
        'libraries': 0,
        'folders': 0,
        'tags': 0,
        'quota': 0,
        'plan': None,
        'uploads_chart': [],
        'size_per_library': [],
        'recent_actions': [],
    }
    if org_id:
        stats['assets'] = (
            db.session.query(db.func.count(Asset.id))
            .join(Library)
            .filter(Library.org_id == org_id)
            .scalar()
            or 0
        )
        stats['storage'] = (
            db.session.query(db.func.sum(Asset.size))
            .join(Library)
            .filter(Library.org_id == org_id)
            .scalar()
            or 0
        )
        stats['libraries'] = Library.query.filter_by(org_id=org_id).count()
        stats['folders'] = (
            db.session.query(db.func.count(Folder.id))
            .join(Library)
            .filter(Library.org_id == org_id)
            .scalar()
            or 0
        )
        stats['tags'] = Tag.query.filter_by(org_id=org_id).count()
        membership = current_user.memberships[0] if current_user.memberships else None
        if membership:
            plan = membership.organization.plan
            stats['plan'] = plan
            stats['quota'] = plan.storage_quota_gb * 1024 * 1024 * 1024
        # uploads in current month grouped by day
        now = datetime.utcnow()
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        uploads = (
            db.session.query(db.func.date(Asset.created_at), db.func.count(Asset.id))
            .join(Library)
            .filter(Library.org_id == org_id, Asset.created_at >= first_day)
            .group_by(db.func.date(Asset.created_at))
            .order_by(db.func.date(Asset.created_at))
            .all()
        )
        stats['uploads_chart'] = [
            {'date': d.strftime('%Y-%m-%d'), 'count': c} for d, c in uploads
        ]
        # storage per library for pie chart
        sizes = (
            db.session.query(Library.name, db.func.sum(Asset.size))
            .join(Asset)
            .filter(Library.org_id == org_id)
            .group_by(Library.name)
            .all()
        )
        stats['size_per_library'] = [
            {'name': name, 'size': size or 0} for name, size in sizes
        ]
        stats['recent_actions'] = (
            AuditLog.query
            .filter_by(org_id=org_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(5)
            .all()
        )
    org = membership.organization if current_user.memberships else None
    return render_template('dashboard/dashboard.html', stats=stats, org=org, title='Dashboard')
