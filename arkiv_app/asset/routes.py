import os
import uuid
import hashlib
from datetime import datetime
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    send_file,
)
from flask_login import login_required, current_user

from ..extensions import db, limiter
from ..models import Asset, Folder, Library
from ..utils.audit import record_audit
from ..utils import role_required
from . import asset_bp
from .forms import AssetUploadForm
from .tasks import generate_thumbnail, perform_ocr


@asset_bp.route("/folders/<int:folder_id>/assets", methods=["GET", "POST"])
@login_required
@limiter.limit("20 per minute")
@role_required("OWNER", "MANAGER", "EDITOR", "CONTRIBUTOR")
def upload_asset(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    form = AssetUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename_storage = f"{uuid.uuid4().hex}_{file.filename}"
        upload_path = current_app.config["UPLOAD_FOLDER"]
        thumb_path = current_app.config["THUMB_FOLDER"]
        os.makedirs(upload_path, exist_ok=True)
        os.makedirs(thumb_path, exist_ok=True)
        filepath = os.path.join(upload_path, filename_storage)
        file.save(filepath)
        size = os.path.getsize(filepath)
        checksum = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
        org = folder.library.organization
        used = (
            db.session.query(db.func.sum(Asset.size))
            .join(Library)
            .filter(Library.org_id == org.id)
            .scalar()
            or 0
        )
        quota = org.plan.storage_quota_gb * 1024 * 1024 * 1024
        if used + size > quota:
            os.remove(filepath)
            flash("Limite de armazenamento excedido!", "error")
            return redirect(url_for("asset.upload_asset", folder_id=folder.id))
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
        record_audit(
            "create", "asset", asset.id, user_id=current_user.id, org_id=org.id
        )
        generate_thumbnail.delay(asset.id, upload_path, thumb_path)
        perform_ocr.delay(asset.id)
        flash("Upload concluído!", "success")
        return redirect(url_for("asset.upload_asset", folder_id=folder.id))
    assets = Asset.query.filter_by(folder_id=folder_id).all()
    return render_template(
        "asset/list.html",
        form=form,
        assets=assets,
        folder=folder,
        title="Arquivos",
    )


@asset_bp.route("/assets/<int:asset_id>")
@login_required
def view_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    return render_template("asset/detail.html", asset=asset, title=asset.filename_orig)


@asset_bp.route("/assets/<int:asset_id>/download")
@login_required
def download_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], asset.filename_storage)
    return send_file(filepath, as_attachment=True, download_name=asset.filename_orig)


@asset_bp.route("/assets/<int:asset_id>/raw")
@login_required
def asset_file(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], asset.filename_storage)
    return send_file(filepath)


@asset_bp.route("/assets/<int:asset_id>/delete", methods=["POST"])
@login_required
@role_required("OWNER", "MANAGER", "EDITOR")
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    asset.deleted_at = datetime.utcnow()
    db.session.commit()
    record_audit("delete", "asset", asset.id, user_id=current_user.id, org_id=asset.folder.library.org_id)
    flash("Asset removido!", "success")
    return redirect(url_for("folder.view_folder", folder_id=asset.folder_id))
