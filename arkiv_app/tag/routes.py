from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Tag, Asset
from ..utils.audit import record_audit
from ..utils import current_org_id
from . import tag_bp
from .forms import TagForm


@tag_bp.route('/tags')
@login_required
def list_tags():
    org_id = current_org_id()
    q = request.args.get('q', '').strip()
    color = request.args.get('color', '').strip()
    sort = request.args.get('sort', 'name')

    tags_query = Tag.query.filter_by(org_id=org_id)
    if q:
        tags_query = tags_query.filter(Tag.name.ilike(f'%{q}%'))
    if color:
        tags_query = tags_query.filter(Tag.color_hex == color)

    if sort == 'usage':
        tags_query = (
            tags_query.outerjoin(Tag.assets)
            .group_by(Tag.id)
            .order_by(db.func.count(Asset.id).desc(), Tag.name.asc())
        )
    else:
        tags_query = tags_query.order_by(Tag.name.asc())

    result = []
    for tag in tags_query.all():
        result.append({'instance': tag, 'asset_count': len(tag.assets)})

    colors = sorted({t.color_hex for t in Tag.query.filter_by(org_id=org_id).all()})

    return render_template(
        'tag/list.html',
        tags=result,
        colors=colors,
        q=q,
        color=color,
        sort=sort,
        title='Tags da Organização'
    )


@tag_bp.route('/tags/create', methods=['GET', 'POST'])
@login_required
def create_tag():
    form = TagForm()
    if form.validate_on_submit():
        org_id = current_org_id()
        tag = Tag(org_id=org_id, name=form.name.data, color_hex=form.color_hex.data or '#CCCCCC')
        db.session.add(tag)
        db.session.commit()
        record_audit('create', 'tag', tag.id, user_id=current_user.id, org_id=org_id)
        flash('Tag criada')
        return redirect(url_for('tag.list_tags'))
    return render_template('tag/form.html', form=form, title='Nova Tag')


@tag_bp.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    form = TagForm(original=tag, obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.color_hex = form.color_hex.data
        db.session.commit()
        record_audit('update', 'tag', tag.id, user_id=current_user.id, org_id=current_org_id())
        flash('Tag atualizada')
        return redirect(url_for('tag.list_tags'))
    return render_template('tag/form.html', form=form, title='Editar Tag')


@tag_bp.route('/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    record_audit('delete', 'tag', tag.id, user_id=current_user.id, org_id=current_org_id())
    flash('Tag removida')
    return redirect(url_for('tag.list_tags'))


@tag_bp.route('/assets/<int:asset_id>/tags', methods=['POST'])
@login_required
def set_asset_tags(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    tag_ids = request.form.getlist('tag_ids')
    asset.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.commit()
    flash('Tags atualizadas')
    return redirect(request.referrer or url_for('asset.upload_asset', folder_id=asset.folder_id))
