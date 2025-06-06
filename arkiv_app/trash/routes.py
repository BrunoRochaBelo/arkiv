import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Asset, Library
from ..utils import current_org_id
from ..utils.audit import record_audit
from . import trash_bp


@trash_bp.route('/')
@login_required
def list_trash():
    org_id = current_org_id()
    assets = (
        Asset.query
        .join(Library)
        .filter(Library.org_id == org_id, Asset.deleted_at.isnot(None))
        .order_by(Asset.deleted_at.desc())
        .all()
    )
    retention_days = current_app.config.get('TRASH_RETENTION_DAYS', 30)
    now = datetime.utcnow()
    return render_template(
        'trash/list.html',
        assets=assets,
        retention_days=retention_days,
        now=now,
        title='Lixeira'
    )


@trash_bp.route('/assets/<int:asset_id>/restore', methods=['POST'])
@login_required
def restore_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    org_id = current_org_id()
    if asset.folder.library.org_id != org_id or not asset.deleted_at:
        flash('Ação inválida')
        return redirect(url_for('trash.list_trash'))
    asset.deleted_at = None
    db.session.commit()
    record_audit('restore', 'asset', asset.id, user_id=current_user.id, org_id=org_id)
    flash('Arquivo restaurado!')
    return redirect(url_for('trash.list_trash'))


@trash_bp.route('/assets/<int:asset_id>/purge', methods=['POST'])
@login_required
def purge_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    org_id = current_org_id()
    if asset.folder.library.org_id != org_id or not asset.deleted_at:
        flash('Ação inválida')
        return redirect(url_for('trash.list_trash'))
    upload_path = current_app.config['UPLOAD_FOLDER']
    thumb_path = current_app.config['THUMB_FOLDER']
    try:
        os.remove(os.path.join(upload_path, asset.filename_storage))
    except FileNotFoundError:
        pass
    try:
        os.remove(os.path.join(thumb_path, asset.filename_storage))
    except FileNotFoundError:
        pass
    db.session.delete(asset)
    db.session.commit()
    record_audit('purge', 'asset', asset.id, user_id=current_user.id, org_id=org_id)
    flash('Arquivo excluído permanentemente!')
    return redirect(url_for('trash.list_trash'))
