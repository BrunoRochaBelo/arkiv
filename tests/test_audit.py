from arkiv_app.extensions import db
from arkiv_app.models import AuditLog


def test_audit_log_on_library_creation(client, app):
    client.post('/login', data={'email': 'test@example.com', 'password': 'test'}, follow_redirects=True)
    res = client.post('/libraries/create', data={'name': 'Lib1', 'description': 'desc'}, follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        assert AuditLog.query.filter_by(action='create', entity='library').count() == 1
