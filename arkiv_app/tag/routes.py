from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Tag, Asset
from . import tag_bp
from .forms import TagForm


@tag_bp.route('/tags')
@login_required
def list_tags():
    org_id = current_user.memberships[0].org_id
    tags = Tag.query.filter_by(org_id=org_id).all()
    return render_template('tag/list.html', tags=tags)


@tag_bp.route('/tags/create', methods=['GET', 'POST'])
@login_required
def create_tag():
    form = TagForm()
    if form.validate_on_submit():
        org_id = current_user.memberships[0].org_id
        tag = Tag(org_id=org_id, name=form.name.data, color_hex=form.color_hex.data or '#CCCCCC')
        db.session.add(tag)
        db.session.commit()
        flash('Tag created')
        return redirect(url_for('tag.list_tags'))
    return render_template('tag/form.html', form=form)


@tag_bp.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.color_hex = form.color_hex.data
        db.session.commit()
        flash('Tag updated')
        return redirect(url_for('tag.list_tags'))
    return render_template('tag/form.html', form=form)


@tag_bp.route('/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted')
    return redirect(url_for('tag.list_tags'))


@tag_bp.route('/assets/<int:asset_id>/tags', methods=['POST'])
@login_required
def set_asset_tags(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    tag_ids = request.form.getlist('tag_ids')
    asset.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.commit()
    flash('Tags updated')
    return redirect(request.referrer or url_for('asset.upload_asset', folder_id=asset.folder_id))
