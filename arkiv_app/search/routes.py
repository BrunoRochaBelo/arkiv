from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from ..utils import current_org_id

from ..models import Asset, Library, Folder
from . import search_bp


@search_bp.route('/search')
@login_required
def search_page():
    """Renderiza a tela de busca global."""
    if request.headers.get('HX-Request'):
        return render_template('search/_global_partial.html')
    return render_template('search/global.html', title='Busca Global')


@search_bp.route('/api/search')
@login_required
def api_search():
    q = request.args.get('q', '')
    only_type = request.args.get('type')
    org_id = current_org_id()
    results = []
    if q:
        like = f"%{q}%"
        if not only_type or only_type == 'asset':
            assets = Asset.query.join(Library).filter(
                Library.org_id == org_id,
                Asset.filename_orig.ilike(like)
            ).all()
            for a in assets:
                results.append({'type': 'asset', 'id': a.id, 'name': a.filename_orig})
        if not only_type or only_type == 'folder':
            folders = Folder.query.join(Library).filter(
                Library.org_id == org_id,
                Folder.name.ilike(like)
            ).all()
            for f in folders:
                results.append({'type': 'folder', 'id': f.id, 'name': f.name})
        if not only_type or only_type == 'library':
            libs = Library.query.filter_by(org_id=org_id).filter(
                Library.name.ilike(like)
            ).all()
            for l in libs:
                results.append({'type': 'library', 'id': l.id, 'name': l.name})
    return jsonify(success=True, data=results)
