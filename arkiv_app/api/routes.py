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
    if not user or user.password_hash != password:
        return jsonify(success=False, message='Invalid credentials'), 401

    token = create_access_token(identity=user.id)
    return jsonify(success=True, data={'access_token': token}, message='Login successful')


@api_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify(success=False, message='User not found'), 404
    data = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
    }
    return jsonify(success=True, data=data)


@api_bp.route('/libraries', methods=['GET'])
@jwt_required()
def list_libraries():
    libs = Library.query.all()
    data = [ {'id': l.id, 'name': l.name, 'description': l.description} for l in libs ]
    return jsonify(success=True, data=data)


@api_bp.route('/libraries', methods=['POST'])
@jwt_required()
def create_library():
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description', '')
    if not name:
        return jsonify(success=False, message='Name required'), 400
    lib = Library(name=name, description=description, org_id=1)
    db.session.add(lib)
    db.session.commit()
    result = {'id': lib.id, 'name': lib.name, 'description': lib.description}
    return jsonify(success=True, data=result), 201
