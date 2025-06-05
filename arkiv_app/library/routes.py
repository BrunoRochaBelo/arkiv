from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..extensions import db
from ..utils.audit import record_audit
from ..models import Library, Folder
from . import library_bp
from .forms import LibraryForm


@library_bp.route("/libraries")
@login_required
def list_libraries():
    libs = Library.query.filter_by(org_id=current_user.memberships[0].org_id).all()
    return render_template("library/list.html", libraries=libs)


@library_bp.route("/libraries/<int:lib_id>")
@login_required
def show_library(lib_id):
    lib = Library.query.get_or_404(lib_id)
    folders = Folder.query.filter_by(library_id=lib_id, parent_id=None).all()
    return render_template("library/detail.html", library=lib, folders=folders)


@library_bp.route("/libraries/create", methods=["GET", "POST"])
@login_required
def create_library():
    form = LibraryForm()
    if form.validate_on_submit():
        org_id = current_user.memberships[0].org_id
        lib = Library(
            org_id=org_id, name=form.name.data, description=form.description.data
        )
        db.session.add(lib)
        db.session.commit()
        record_audit(
            "create", "library", lib.id, user_id=current_user.id, org_id=org_id
        )
        flash("Biblioteca criada")
        return redirect(url_for("library.list_libraries"))
    return render_template("library/form.html", form=form)


@library_bp.route("/libraries/<int:lib_id>/edit", methods=["GET", "POST"])
@login_required
def edit_library(lib_id):
    lib = Library.query.get_or_404(lib_id)
    form = LibraryForm(obj=lib)
    if form.validate_on_submit():
        lib.name = form.name.data
        lib.description = form.description.data
        db.session.commit()
        record_audit(
            "update",
            "library",
            lib.id,
            user_id=current_user.id,
            org_id=current_user.memberships[0].org_id,
        )
        flash("Biblioteca atualizada")
        return redirect(url_for("library.list_libraries"))
    return render_template("library/form.html", form=form)


@library_bp.route("/libraries/<int:lib_id>/delete", methods=["POST"])
@login_required
def delete_library(lib_id):
    lib = Library.query.get_or_404(lib_id)
    db.session.delete(lib)
    db.session.commit()
    record_audit(
        "delete",
        "library",
        lib.id,
        user_id=current_user.id,
        org_id=current_user.memberships[0].org_id,
    )
    flash("Biblioteca removida")
    return redirect(url_for("library.list_libraries"))
