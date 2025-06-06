from arkiv_app.extensions import db
from arkiv_app.models import Library, Folder, Asset


def login(client):
    client.post('/login', data={'email': 'test@example.com', 'password': 'test'}, follow_redirects=True)


def test_search_page_loads(client):
    login(client)
    res = client.get('/search')
    assert res.status_code == 200
    assert b'Buscar por nome, tag, tipo, usu\xc3\xa1rio' in res.data


def test_search_api_basic(client, app):
    login(client)
    with app.app_context():
        lib = Library(org_id=1, name='Lib', description='d')
        folder = Folder(name='F', library=lib)
        asset = Asset(
            library=lib,
            folder=folder,
            uploader_id=1,
            filename_orig='img.png',
            filename_storage='img.png',
            mime='image/png',
            size=1,
            checksum_sha256='x'
        )
        db.session.add_all([lib, folder, asset])
        db.session.commit()
    res = client.get('/api/search?q=img')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert any(r['type'] == 'asset' for r in data['data'])
