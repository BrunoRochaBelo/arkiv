from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Library, Folder
from . import folder_bp
from .forms import FolderForm


def _populate_form_choices(form):
    org_id = current_user.memberships[0].org_id
    libs = Library.query.filter_by(org_id=org_id).all()
    form.library_id.choices = [(l.id, l.name) for l in libs]
    # For parent folder, show only within selected library
    form.parent_id.choices = [(0, 'Root')] + [
        (f.id, f.name) for f in Folder.query.filter_by(library_id=form.library_id.data or libs[0].id).all()
    ]


@folder_bp.route('/folders/create', methods=['GET', 'POST'])
@login_required
def create_folder():
    form = FolderForm()
    _populate_form_choices(form)
    if form.validate_on_submit():
        parent_id = form.parent_id.data or None
        folder = Folder(
            library_id=form.library_id.data,
            parent_id=parent_id if parent_id != 0 else None,
            name=form.name.data,
        )
        db.session.add(folder)
        db.session.commit()
        flash('Folder created')
        return redirect(url_for('library.list_libraries'))
    return render_template('folder/form.html', form=form)


@folder_bp.route('/folders/<int:folder_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    form = FolderForm(obj=folder)
    _populate_form_choices(form)
    if form.validate_on_submit():
        folder.library_id = form.library_id.data
        folder.parent_id = form.parent_id.data or None
        folder.name = form.name.data
        db.session.commit()
        flash('Folder updated')
        return redirect(url_for('library.list_libraries'))
    return render_template('folder/form.html', form=form)


@folder_bp.route('/folders/<int:folder_id>/delete', methods=['POST'])
@login_required
def delete_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    db.session.delete(folder)
    db.session.commit()
    flash('Folder deleted')
    return redirect(url_for('library.list_libraries'))
