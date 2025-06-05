from flask import render_template
from flask_login import login_required

from ..models import Organization, Plan
from . import admin_bp

@admin_bp.route('/plans')
@login_required
def list_plans():
    plans = Plan.query.all()
    return render_template('admin/plans.html', plans=plans)

@admin_bp.route('/orgs')
@login_required
def list_orgs():
    orgs = Organization.query.all()
    return render_template('admin/orgs.html', orgs=orgs)
