from arkiv_app.extensions import db
from arkiv_app.models import Poll, PollOption


def test_poll_create_and_vote(client, app):
    client.post('/login', data={'email': 'test@example.com', 'password': 'test'}, follow_redirects=True)
    with app.app_context():
        poll = Poll(org_id=1, creator_id=1, question='Pergunta')
        db.session.add(poll)
        db.session.flush()
        opt = PollOption(poll_id=poll.id, text='Op1')
        db.session.add(opt)
        db.session.commit()
        poll_id = poll.id
        option_id = opt.id
    res = client.post(f'/polls/{poll_id}/vote/{option_id}', follow_redirects=True)
    assert res.status_code == 200
