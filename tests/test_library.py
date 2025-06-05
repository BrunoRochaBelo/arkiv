from arkiv_app.extensions import db
from arkiv_app.models import Library


def test_library_detail_view(client, app):
    client.post(
        "/login",
        data={"email": "test@example.com", "password": "test"},
        follow_redirects=True,
    )
    with app.app_context():
        lib = Library(org_id=1, name="Demo", description="desc")
        db.session.add(lib)
        db.session.commit()
        lib_id = lib.id
    res = client.get(f"/libraries/{lib_id}")
    assert res.status_code == 200
    assert b"Demo" in res.data
