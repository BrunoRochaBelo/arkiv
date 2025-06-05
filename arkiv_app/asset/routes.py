import os
import uuid
import hashlib
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from ..extensions import db, limiter
from ..models import Asset, Folder, Library
from ..utils.audit import record_audit
from . import asset_bp
from .forms import AssetUploadForm
from .tasks import generate_thumbnail, perform_ocr





@asset_bp.route('/folders/<int:folder_id>/assets', methods=['GET', 'POST'])
@login_required
@limiter.limit('20 per minute')
def upload_asset(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    form = AssetUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename_storage = f"{uuid.uuid4().hex}_{file.filename}"
        upload_path = current_app.config['UPLOAD_FOLDER']
        thumb_path = current_app.config['THUMB_FOLDER']
        os.makedirs(upload_path, exist_ok=True)
        os.makedirs(thumb_path, exist_ok=True)
        filepath = os.path.join(upload_path, filename_storage)
        file.save(filepath)
        size = os.path.getsize(filepath)
        checksum = hashlib.sha256(open(filepath, 'rb').read()).hexdigest()
        org = folder.library.organization
        used = db.session.query(db.func.sum(Asset.size)).join(Library).filter(Library.org_id == org.id).scalar() or 0
        quota = org.plan.storage_quota_gb * 1024 * 1024 * 1024
        if used + size > quota:
            os.remove(filepath)
            flash('Storage quota exceeded')
            return redirect(url_for('library.list_libraries'))
        asset = Asset(
            library_id=folder.library_id,
            folder_id=folder.id,
            uploader_id=current_user.id,
            filename_orig=file.filename,
            filename_storage=filename_storage,
            mime=file.mimetype,
            size=size,
            checksum_sha256=checksum,
        )
        db.session.add(asset)
        db.session.commit()
        record_audit('create', 'asset', asset.id, user_id=current_user.id, org_id=org.id)
        generate_thumbnail.delay(asset.id, upload_path, thumb_path)
        perform_ocr.delay(asset.id)
        flash('File uploaded')
        return redirect(url_for('library.list_libraries'))
    assets = Asset.query.filter_by(folder_id=folder_id).all()
    return render_template('asset/list.html', form=form, assets=assets, folder=folder)
