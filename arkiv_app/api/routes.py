import os
import uuid
import hashlib
from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from ..extensions import db
from ..models import User, Library, Folder, Asset, Tag
from . import api_bp


@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify(success=False, message='Email and password required'), 400

    user = User.query.filter_by(email=email).first()
    # Sempre use verificação de senha via método seguro!
    if not user or not user.check_password(password):
        return jsonify(success=False, message='Invalid credentials'), 401

    token = create_access_token(identity=user.id)
    return jsonify(success=True, data={'access_token': token}, message='Login successful')


@api_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def profile():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify(success=False, message='User not found'), 404

    membership = user.memberships[0] if user.memberships else None

    data = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'org_id': membership.org_id if membership else None,
        'role': membership.role if membership else None,
    }
    return jsonify(success=True, data=data)


@api_bp.route('/libraries', methods=['GET'])
@jwt_required()
def list_libraries():
    libs = Library.query.all()
    data = [{'id': l.id, 'name': l.name, 'description': l.description} for l in libs]
    return jsonify(success=True, data=data)


@api_bp.route('/libraries', methods=['POST'])
@jwt_required()
def create_library():
    user = User.query.get(get_jwt_identity())
    membership = user.memberships[0] if user and user.memberships else None
    if not membership:
        return jsonify(success=False, message='User has no organization'), 400

    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify(success=False, message='Name required'), 400
    description = data.get('description', '')
    lib = Library(org_id=membership.org_id, name=name, description=description)
    db.session.add(lib)
    db.session.commit()
    return (
        jsonify(
            success=True,
            data={'id': lib.id, 'name': lib.name, 'description': lib.description},
            message='Library created',
        ),
        201,
    )


@api_bp.route('/tags', methods=['GET'])
@jwt_required()
def list_tags_api():
    user = User.query.get(get_jwt_identity())
    membership = user.memberships[0] if user and user.memberships else None
    if not membership:
        return jsonify(success=False, message='User has no organization'), 400
    tags = Tag.query.filter_by(org_id=membership.org_id).all()
    data = [{'id': t.id, 'name': t.name, 'color_hex': t.color_hex} for t in tags]
    return jsonify(success=True, data=data)


@api_bp.route('/tags', methods=['POST'])
@jwt_required()
def create_tag_api():
    user = User.query.get(get_jwt_identity())
    membership = user.memberships[0] if user and user.memberships else None
    if not membership:
        return jsonify(success=False, message='User has no organization'), 400
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify(success=False, message='Name required'), 400
    color = data.get('color_hex', '#CCCCCC')
    tag = Tag(org_id=membership.org_id, name=name, color_hex=color)
    db.session.add(tag)
    db.session.commit()
    return jsonify(success=True, data={'id': tag.id, 'name': tag.name, 'color_hex': tag.color_hex}, message='Tag created'), 201


@api_bp.route('/tags/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag_api(tag_id):
    user = User.query.get(get_jwt_identity())
    membership = user.memberships[0] if user and user.memberships else None
    if not membership:
        return jsonify(success=False, message='User has no organization'), 400
    tag = Tag.query.get_or_404(tag_id)
    data = request.get_json() or {}
    tag.name = data.get('name', tag.name)
    tag.color_hex = data.get('color_hex', tag.color_hex)
    db.session.commit()
    return jsonify(success=True, data={'id': tag.id, 'name': tag.name, 'color_hex': tag.color_hex}, message='Tag updated')


@api_bp.route('/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag_api(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return jsonify(success=True, message='Tag deleted')


@api_bp.route('/assets/<int:asset_id>/tags', methods=['POST'])
@jwt_required()
def set_asset_tags_api(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    data = request.get_json() or {}
    tag_ids = data.get('tag_ids', [])
    asset.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    db.session.commit()
    return jsonify(success=True, message='Tags updated')


@api_bp.route('/search', methods=['GET'])
@jwt_required()
def search_api():
    q = request.args.get('q', '')
    user = User.query.get(get_jwt_identity())
    membership = user.memberships[0] if user and user.memberships else None
    if not membership:
        return jsonify(success=False, message='User has no organization'), 400
    results = []
    if q:
        like = f"%{q}%"
        assets = Asset.query.join(Library).filter(Library.org_id == membership.org_id, Asset.filename_orig.ilike(like)).all()
        folders = Folder.query.join(Library).filter(Library.org_id == membership.org_id, Folder.name.ilike(like)).all()
        libs = Library.query.filter_by(org_id=membership.org_id).filter(Library.name.ilike(like)).all()
        for a in assets:
            results.append({'type': 'asset', 'id': a.id, 'name': a.filename_orig})
        for f in folders:
            results.append({'type': 'folder', 'id': f.id, 'name': f.name})
        for l in libs:
            results.append({'type': 'library', 'id': l.id, 'name': l.name})
    return jsonify(success=True, data=results)


@api_bp.route('/libraries/<int:lib_id>/folders', methods=['GET'])
@jwt_required()
def list_folders_api(lib_id):
    folders = Folder.query.filter_by(library_id=lib_id).all()
    data = [{'id': f.id, 'name': f.name, 'parent_id': f.parent_id} for f in folders]
    return jsonify(success=True, data=data)


@api_bp.route('/folders', methods=['POST'])
@jwt_required()
def create_folder_api():
    data = request.get_json() or {}
    library_id = data.get('library_id')
    name = data.get('name')
    parent_id = data.get('parent_id')
    if not library_id or not name:
        return jsonify(success=False, message='library_id and name required'), 400
    folder = Folder(library_id=library_id, parent_id=parent_id, name=name)
    db.session.add(folder)
    db.session.commit()
    return jsonify(success=True, data={'id': folder.id, 'name': folder.name}, message='Folder created'), 201


@api_bp.route('/folders/<int:folder_id>', methods=['PUT'])
@jwt_required()
def update_folder_api(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    data = request.get_json() or {}
    folder.name = data.get('name', folder.name)
    folder.parent_id = data.get('parent_id', folder.parent_id)
    db.session.commit()
    return jsonify(success=True, data={'id': folder.id, 'name': folder.name}, message='Folder updated')


@api_bp.route('/folders/<int:folder_id>', methods=['DELETE'])
@jwt_required()
def delete_folder_api(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    db.session.delete(folder)
    db.session.commit()
    return jsonify(success=True, message='Folder deleted')


@api_bp.route('/folders/<int:folder_id>/assets', methods=['GET'])
@jwt_required()
def list_assets_api(folder_id):
    assets = Asset.query.filter_by(folder_id=folder_id).all()
    data = [{'id': a.id, 'filename_orig': a.filename_orig} for a in assets]
    return jsonify(success=True, data=data)


@api_bp.route('/folders/<int:folder_id>/assets', methods=['POST'])
@jwt_required()
def upload_asset_api(folder_id):
    folder = Folder.query.get_or_404(folder_id)
    file = request.files.get('file')
    if not file:
        return jsonify(success=False, message='file required'), 400
    filename_storage = f"{uuid.uuid4().hex}_{file.filename}"
    upload_path = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_path, exist_ok=True)
    filepath = os.path.join(upload_path, filename_storage)
    file.save(filepath)
    size = os.path.getsize(filepath)
    checksum = hashlib.sha256(open(filepath, 'rb').read()).hexdigest()
    asset = Asset(
        library_id=folder.library_id,
        folder_id=folder.id,
        uploader_id=get_jwt_identity(),
        filename_orig=file.filename,
        filename_storage=filename_storage,
        mime=file.mimetype,
        size=size,
        checksum_sha256=checksum,
    )
    db.session.add(asset)
    db.session.commit()
    return jsonify(success=True, data={'id': asset.id, 'filename_orig': asset.filename_orig}, message='Asset uploaded'), 201
