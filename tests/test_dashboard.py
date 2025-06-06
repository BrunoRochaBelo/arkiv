from arkiv_app.extensions import db
from arkiv_app.models import Library, Folder, Asset

def test_dashboard_view(client, app):
    client.post('/login', data={'email': 'test@example.com', 'password': 'test'}, follow_redirects=True)
    with app.app_context():
        lib = Library(org_id=1, name='Lib')
        folder = Folder(name='F', library=lib)
        asset = Asset(
            library=lib,
            folder=folder,
            uploader_id=1,
            filename_orig='a.png',
            filename_storage='a.png',
            mime='image/png',
            size=1,
            checksum_sha256='x'
        )
        db.session.add_all([lib, folder, asset])
        db.session.commit()
    res = client.get('/dashboard/')
    assert res.status_code == 200
    assert b'Dashboard' in res.data
