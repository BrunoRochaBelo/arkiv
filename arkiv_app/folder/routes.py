from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..utils import current_org_id, role_required

from ..extensions import db
from ..models import Library, Folder
from ..utils.audit import record_audit
from . import folder_bp
from .forms import FolderForm


def _populate_form_choices(form, libs):
    form.library_id.choices = [(l.id, l.name) for l in libs]
    selected = form.library_id.data or (libs[0].id if libs else None)
    if selected:
        form.parent_id.choices = [(0, "Raiz")] + [
            (f.id, f.name) for f in Folder.query.filter_by(library_id=selected).all()
        ]
    else:
        form.parent_id.choices = [(0, "Raiz")]


@folder_bp.route("/folders/create", methods=["GET", "POST"])
@login_required
@role_required("OWNER", "MANAGER", "EDITOR", "CONTRIBUTOR")
def create_folder():
    form = FolderForm()
    org_id = current_org_id()
    libs = Library.query.filter_by(org_id=org_id).all()
    if not libs:
        flash("Crie uma biblioteca antes de adicionar pastas")
        return redirect(url_for("library.create_library"))
    if request.args.get("library_id"):
        form.library_id.data = int(request.args["library_id"])
    if request.args.get("parent_id"):
        form.parent_id.data = int(request.args["parent_id"])
    _populate_form_choices(form, libs)
    if form.validate_on_submit():
        parent_id = form.parent_id.data or None
        folder = Folder(
            library_id=form.library_id.data,
            parent_id=parent_id if parent_id != 0 else None,
            name=form.name.data,
        )
        db.session.add(folder)
        db.session.commit()
        record_audit(
            "create",
            "folder",
            folder.id,
            user_id=current_user.id,
            org_id=org_id,
        )
        flash("Pasta criada")
        return redirect(url_for("library.list_libraries"))
    return render_template("folder/form.html", form=form, title="Nova Pasta")


@folder_bp.route("/folders/<int:folder_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("OWNER", "MANAGER", "EDITOR")
def edit_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    form = FolderForm(obj=folder)
    org_id = current_org_id()
    libs = Library.query.filter_by(org_id=org_id).all()
    if not libs:
        flash("Crie uma biblioteca antes de adicionar pastas")
        return redirect(url_for("library.create_library"))
    _populate_form_choices(form, libs)
    if form.validate_on_submit():
        folder.library_id = form.library_id.data
        folder.parent_id = form.parent_id.data or None
        folder.name = form.name.data
        db.session.commit()
        record_audit(
            "update",
            "folder",
            folder.id,
            user_id=current_user.id,
            org_id=org_id,
        )
        flash("Pasta atualizada")
        return redirect(url_for("library.list_libraries"))
    return render_template("folder/form.html", form=form, title="Editar Pasta")


@folder_bp.route("/folders/<int:folder_id>/delete", methods=["POST"])
@login_required
@role_required("OWNER", "MANAGER", "EDITOR")
def delete_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    db.session.delete(folder)
    db.session.commit()
    record_audit(
        "delete",
        "folder",
        folder.id,
        user_id=current_user.id,
        org_id=current_org_id(),
    )
    flash("Pasta removida")
    return redirect(url_for("library.list_libraries"))


@folder_bp.route("/folders/<int:folder_id>")
@login_required
def view_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    subfolders = Folder.query.filter_by(parent_id=folder.id).all()
    return render_template(
        "folder/detail.html",
        folder=folder,
        subfolders=subfolders,
        title=folder.name,
    )
