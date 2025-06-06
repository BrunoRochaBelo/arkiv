from flask import render_template, abort
from flask_login import login_required, current_user

from ..models import Organization, Plan, User, AuditLog
from . import admin_bp

def _staff_required():
    if not current_user.is_authenticated or not current_user.is_staff:
        abort(403)

@admin_bp.route('/plans')
@login_required
def list_plans():
    _staff_required()
    plans = Plan.query.all()
    return render_template('admin/plans.html', plans=plans, title='Planos')

@admin_bp.route('/orgs')
@login_required
def list_orgs():
    _staff_required()
    orgs = Organization.query.all()
    return render_template('admin/orgs.html', orgs=orgs, title='Organizações')


@admin_bp.route('/users')
@login_required
def list_users():
    _staff_required()
    users = User.query.all()
    return render_template('admin/users.html', users=users, title='Usuários')


@admin_bp.route('/logs')
@login_required
def list_logs():
    _staff_required()
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin/logs.html', logs=logs, title='Auditoria')


@admin_bp.route('/')
@login_required
def index():
    _staff_required()
    return render_template('admin/index.html', title='Admin')
