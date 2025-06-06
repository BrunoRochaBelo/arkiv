from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..utils import current_org_id

from ..extensions import db
from ..utils.audit import record_audit
from ..models import Library, Folder, Asset
from . import library_bp
from .forms import LibraryForm


@library_bp.route("/libraries")
@login_required
def list_libraries():
    org_id = current_org_id()
    q = request.args.get("q", "")
    libs_query = Library.query.filter_by(org_id=org_id) if org_id else Library.query.filter(False)
    if q:
        like = f"%{q}%"
        libs_query = libs_query.filter(Library.name.ilike(like))
    libs = libs_query.all()

    libraries = []
    for lib in libs:
        asset_count = (
            db.session.query(db.func.count(Asset.id))
            .filter(Asset.library_id == lib.id)
            .scalar()
            or 0
        )
        last_asset = (
            Asset.query
            .filter_by(library_id=lib.id)
            .order_by(Asset.updated_at.desc().nullslast(), Asset.created_at.desc())
            .first()
        )
        last_update = None
        if last_asset:
            last_update = last_asset.updated_at or last_asset.created_at
        thumbs = (
            Asset.query
            .filter_by(library_id=lib.id)
            .order_by(Asset.created_at.desc())
            .limit(4)
            .all()
        )
        libraries.append({
            "instance": lib,
            "asset_count": asset_count,
            "last_update": last_update,
            "thumbs": thumbs,
        })

    return render_template(
        "library/list.html",
        libraries=libraries,
        q=q,
        title="Bibliotecas",
    )


@library_bp.route("/libraries/<int:lib_id>")
@login_required
def show_library(lib_id):
    lib = Library.query.get_or_404(lib_id)
    folders = Folder.query.filter_by(library_id=lib_id, parent_id=None).all()
    return render_template(
        "library/detail.html",
        library=lib,
        folders=folders,
        title=lib.name,
    )


@library_bp.route("/libraries/create", methods=["GET", "POST"])
@login_required
def create_library():
    form = LibraryForm()
    if form.validate_on_submit():
        org_id = current_org_id()
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
    return render_template("library/form.html", form=form, title="Nova Biblioteca")


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
            org_id=current_org_id(),
        )
        flash("Biblioteca atualizada")
        return redirect(url_for("library.list_libraries"))
    return render_template("library/form.html", form=form, title="Editar Biblioteca")


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
        org_id=current_org_id(),
    )
    flash("Biblioteca removida")
    return redirect(url_for("library.list_libraries"))
