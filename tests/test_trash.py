from datetime import datetime
from arkiv_app.extensions import db
from arkiv_app.models import Library, Folder, Asset


def login(client):
    client.post('/login', data={'email': 'test@example.com', 'password': 'test'}, follow_redirects=True)


def setup_asset(app):
    with app.app_context():
        lib = Library(org_id=1, name='Lib', description='d')
        folder = Folder(name='F', library=lib)
        asset = Asset(
            library=lib,
            folder=folder,
            uploader_id=1,
            filename_orig='del.png',
            filename_storage='del.png',
            mime='image/png',
            size=1,
            checksum_sha256='x'
        )
        db.session.add_all([lib, folder, asset])
        db.session.commit()
        return asset.id


def test_trash_view_and_restore(client, app):
    login(client)
    asset_id = setup_asset(app)
    with app.app_context():
        asset = Asset.query.get(asset_id)
        asset.deleted_at = datetime.utcnow()
        db.session.commit()
    res = client.get('/trash/')
    assert res.status_code == 200
    assert b'del.png' in res.data
    res = client.post(f'/trash/assets/{asset_id}/restore', follow_redirects=True)
    assert b'Arquivo restaurado' in res.data
    with app.app_context():
        assert Asset.query.get(asset_id).deleted_at is None


def test_trash_purge(client, app):
    login(client)
    asset_id = setup_asset(app)
    with app.app_context():
        asset = Asset.query.get(asset_id)
        asset.deleted_at = datetime.utcnow()
        db.session.commit()
    res = client.post(f'/trash/assets/{asset_id}/purge', follow_redirects=True)
    assert b'exclu\xc3\xaddo permanentemente' in res.data
    with app.app_context():
        assert Asset.query.get(asset_id) is None
