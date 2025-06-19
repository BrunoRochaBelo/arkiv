from arkiv_app.extensions import db
from arkiv_app.models import Ticket


def test_ticket_list_view(client, app):
    client.post('/login', data={'email': 'test@example.com', 'password': 'test'}, follow_redirects=True)
    with app.app_context():
        ticket = Ticket(org_id=1, creator_id=1, title='Chamado', description='Desc')
        db.session.add(ticket)
        db.session.commit()
    res = client.get('/tickets')
    assert res.status_code == 200
    assert b'Chamado' in res.data
