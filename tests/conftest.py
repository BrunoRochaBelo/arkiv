import os
import sys
import pytest

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("CELERY_ALWAYS_EAGER", "1")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arkiv_app import create_app
from arkiv_app.extensions import db
from arkiv_app.models import Plan, Organization, User, Membership
from arkiv_app.utils.audit import ensure_audit_log_schema

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        ensure_audit_log_schema()
        plan = Plan(name='Test', storage_quota_gb=1, price_monthly=0)
        db.session.add(plan)
        db.session.commit()
        org = Organization(name='TestOrg', slug='testorg', plan_id=plan.id)
        db.session.add(org)
        db.session.commit()
        user = User(name='Test', email='test@example.com')
        user.set_password('test')
        db.session.add(user)
        db.session.commit()
        membership = Membership(user_id=user.id, org_id=org.id, role='OWNER')
        db.session.add(membership)
        db.session.commit()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()
