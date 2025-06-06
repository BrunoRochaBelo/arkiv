import os
from flask import render_template, abort, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Asset, Library, User, Membership
from ..utils import current_org_id, role_required
from .forms import OrganizationForm, InviteUserForm
from . import organization_bp


@organization_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('OWNER', 'MANAGER')
def settings():
    membership = current_user.memberships[0] if current_user.memberships else None

    org = membership.organization
    form = OrganizationForm(name=org.name)

    if form.validate_on_submit():
        org.name = form.name.data
        db.session.commit()
        flash('Configurações salvas')
        return redirect(url_for('organization.settings'))

    used_storage = (
        db.session.query(db.func.sum(Asset.size))
        .join(Library)
        .filter(Library.org_id == org.id)
        .scalar()
        or 0
    )
    quota = org.plan.storage_quota_gb * 1024 * 1024 * 1024

    return render_template(
        'organization/settings.html',
        form=form,
        org=org,
        used_storage=used_storage,
        quota=quota,
        title='Configurações da Organização',
    )


@organization_bp.route('/members', methods=['GET', 'POST'])
@login_required
@role_required('OWNER', 'MANAGER')
def members():
    membership = current_user.memberships[0] if current_user.memberships else None

    org = membership.organization
    invite_form = InviteUserForm()
    if invite_form.validate_on_submit():
        email = invite_form.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=email.split('@')[0], email=email)
            user.set_password(os.urandom(16).hex())
            db.session.add(user)
            db.session.commit()
        if not Membership.query.filter_by(user_id=user.id, org_id=org.id).first():
            m = Membership(user_id=user.id, org_id=org.id, role=invite_form.role.data)
            db.session.add(m)
            db.session.commit()
            flash('Usuário convidado')
        else:
            flash('Usuário já é membro')
        return redirect(url_for('organization.members'))

    q = request.args.get('q', '')
    members_query = (
        Membership.query.filter_by(org_id=org.id).join(User)
    )
    if q:
        like = f'%{q}%'
        members_query = members_query.filter(
            db.or_(User.name.ilike(like), User.email.ilike(like))
        )
    members = members_query.all()

    role_colors = {
        'OWNER': 'purple',
        'MANAGER': 'primary',
        'EDITOR': 'success',
        'CONTRIBUTOR': 'info',
        'VIEWER': 'secondary',
    }
    roles = ['OWNER', 'MANAGER', 'EDITOR', 'CONTRIBUTOR', 'VIEWER']
    return render_template(
        'organization/members.html',
        org=org,
        invite_form=invite_form,
        members=members,
        q=q,
        role_colors=role_colors,
        roles=roles,
        title='Usuários & Permissões',
    )


@organization_bp.route('/members/<int:user_id>/role', methods=['POST'])
@login_required
@role_required('OWNER', 'MANAGER')
def update_member_role(user_id):
    membership = current_user.memberships[0] if current_user.memberships else None
    org = membership.organization
    new_role = request.form.get('role')
    mem = Membership.query.filter_by(user_id=user_id, org_id=org.id).first_or_404()
    if mem.user_id == current_user.id and mem.role == 'OWNER' and new_role != 'OWNER':
        flash('Você não pode rebaixar seu próprio papel de OWNER')
        return redirect(url_for('organization.members'))
    mem.role = new_role
    db.session.commit()
    flash('Permissão alterada!')
    return redirect(url_for('organization.members'))


@organization_bp.route('/members/<int:user_id>/remove', methods=['POST'])
@login_required
@role_required('OWNER', 'MANAGER')
def remove_member(user_id):
    membership = current_user.memberships[0] if current_user.memberships else None
    org = membership.organization
    mem = Membership.query.filter_by(user_id=user_id, org_id=org.id).first_or_404()
    if mem.role == 'OWNER':
        owner_count = Membership.query.filter_by(org_id=org.id, role='OWNER').count()
        if owner_count <= 1:
            flash('Não é possível remover o último OWNER')
            return redirect(url_for('organization.members'))
    db.session.delete(mem)
    db.session.commit()
    flash('Usuário removido')
    return redirect(url_for('organization.members'))
