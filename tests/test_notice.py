from arkiv_app.extensions import db
from arkiv_app.models import Notice


def test_notice_list_view(client, app):
    client.post('/login', data={'email': 'test@example.com', 'password': 'test'}, follow_redirects=True)
    with app.app_context():
        notice = Notice(org_id=1, user_id=1, title='Aviso', body='Corpo')
        db.session.add(notice)
        db.session.commit()
        notice_id = notice.id
    res = client.get('/notices')
    assert res.status_code == 200
    assert b'Aviso' in res.data
