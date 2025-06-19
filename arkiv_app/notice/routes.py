from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Notice
from ..utils.audit import record_audit
from ..utils import current_org_id
from . import notice_bp
from .forms import NoticeForm


@notice_bp.route('/notices')
@login_required
def list_notices():
    org_id = current_org_id()
    notices = Notice.query.filter_by(org_id=org_id).order_by(Notice.created_at.desc()).all()
    return render_template('notice/list.html', notices=notices, title='Mural')


@notice_bp.route('/notices/create', methods=['GET', 'POST'])
@login_required
def create_notice():
    form = NoticeForm()
    if form.validate_on_submit():
        org_id = current_org_id()
        notice = Notice(
            org_id=org_id,
            user_id=current_user.id,
            title=form.title.data,
            body=form.body.data,
            category=form.category.data,
        )
        db.session.add(notice)
        db.session.commit()
        record_audit('create', 'notice', notice.id, user_id=current_user.id, org_id=org_id)
        flash('Aviso criado', 'success')
        return redirect(url_for('notice.list_notices'))
    return render_template('notice/form.html', form=form, title='Novo Aviso')
