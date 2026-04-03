from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models.user import User
from .. import db


users_bp = Blueprint('users', __name__)


def _current_user():
    identity = get_jwt_identity()
    return User.query.get(identity['id'])


def _require_admin(user):
    if not user or user.role != 'admin':
        return jsonify({'message': 'Admin privileges required'}), 403
    return None


@users_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    user = _current_user()
    err = _require_admin(user)
    if err:
        return err
    users = User.query.all()
    return jsonify({'items': [u.to_dict() for u in users]}), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = _current_user()
    err = _require_admin(user)
    if err:
        return err
    u = User.query.get_or_404(user_id)
    return jsonify(u.to_dict()), 200


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    user = _current_user()
    err = _require_admin(user)
    if err:
        return err
    u = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    role = data.get('role')
    if role:
        u.role = role
    db.session.commit()
    return jsonify(u.to_dict()), 200


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = _current_user()
    err = _require_admin(user)
    if err:
        return err
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200
