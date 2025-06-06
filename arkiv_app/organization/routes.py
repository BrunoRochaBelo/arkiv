from flask import render_template, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Asset, Library
from ..utils import current_org_id
from .forms import OrganizationForm
from . import organization_bp


@organization_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    membership = current_user.memberships[0] if current_user.memberships else None
    if not membership or membership.role not in ('OWNER', 'MANAGER'):
        abort(403)

    org = membership.organization
    form = OrganizationForm(name=org.name)

    if form.validate_on_submit():
        org.name = form.name.data
        db.session.commit()
        flash('Configurações salvas')
        return redirect(url_for('organization.settings'))

    used_storage = (
        db.session.query(db.func.sum(Asset.size))
        .join(Library)
        .filter(Library.org_id == org.id)
        .scalar()
        or 0
    )
    quota = org.plan.storage_quota_gb * 1024 * 1024 * 1024

    return render_template(
        'organization/settings.html',
        form=form,
        org=org,
        used_storage=used_storage,
        quota=quota,
        title='Configurações da Organização',
    )
