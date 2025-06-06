from arkiv_app.extensions import db
from arkiv_app.models import Membership, User


def login(client):
    client.post('/login', data={'email': 'test@example.com', 'password': 'test'}, follow_redirects=True)


def test_members_page(client):
    login(client)
    res = client.get('/org/members')
    assert res.status_code == 200
    assert b'Usu\xc3\xa1rios & Permiss\xc3\xb5es' in res.data


def test_invite_member(client, app):
    login(client)
    with app.app_context():
        count_before = Membership.query.count()
    res = client.post('/org/members', data={'email': 'new@example.com', 'role': 'VIEWER'}, follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        assert Membership.query.count() == count_before + 1
        assert User.query.filter_by(email='new@example.com').first() is not None
