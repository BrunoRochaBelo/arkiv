from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from ..extensions import db
from ..models import User, Library
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
