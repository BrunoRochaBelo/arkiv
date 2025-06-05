from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from ..models import Asset, Library, Folder
from . import search_bp


@search_bp.route('/search')
@login_required
def search_page():
    q = request.args.get('q', '')
    org_id = current_user.memberships[0].org_id
    assets = []
    folders = []
    libs = []
    if q:
        like = f"%{q}%"
        assets = Asset.query.join(Library).filter(Library.org_id == org_id, Asset.filename_orig.ilike(like)).all()
        folders = Folder.query.join(Library).filter(Library.org_id == org_id, Folder.name.ilike(like)).all()
        libs = Library.query.filter_by(org_id=org_id).filter(Library.name.ilike(like)).all()
    return render_template('search/results.html', assets=assets, folders=folders, libraries=libs, query=q)


@search_bp.route('/api/search')
@login_required
def api_search():
    q = request.args.get('q', '')
    org_id = current_user.memberships[0].org_id
    results = []
    if q:
        like = f"%{q}%"
        assets = Asset.query.join(Library).filter(Library.org_id == org_id, Asset.filename_orig.ilike(like)).all()
        for a in assets:
            results.append({'type': 'asset', 'id': a.id, 'name': a.filename_orig})
        folders = Folder.query.join(Library).filter(Library.org_id == org_id, Folder.name.ilike(like)).all()
        for f in folders:
            results.append({'type': 'folder', 'id': f.id, 'name': f.name})
        libs = Library.query.filter_by(org_id=org_id).filter(Library.name.ilike(like)).all()
        for l in libs:
            results.append({'type': 'library', 'id': l.id, 'name': l.name})
    return jsonify(success=True, data=results)
