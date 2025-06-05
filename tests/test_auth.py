from flask_login import current_user


def test_login_creates_session(client):
    res = client.post('/login', data={'email': 'test@example.com', 'password': 'test'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'Biblioteca' in res.data or b'Bibliotecas' in res.data
