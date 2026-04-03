from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models.user import User
from ..services.transaction_service import (
    get_transactions_for_user,
    get_transaction_for_user,
    create_transaction_for_user,
    update_transaction_for_user,
    delete_transaction_for_user,
)


transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('', methods=['GET'])
@jwt_required()
def list_transactions():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    filters = request.args.to_dict()
    page = int(filters.pop('page', 1))
    per_page = int(filters.pop('per_page', 50))

    items, pagination = get_transactions_for_user(user, filters, page, per_page)

    return jsonify({
        'items': [t.to_dict() for t in items],
        'page': pagination['page'],
        'per_page': pagination['per_page'],
        'total': pagination['total'],
    }), 200


@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    tx = get_transaction_for_user(user, transaction_id)
    if not tx:
        return jsonify({'message': 'Transaction not found'}), 404
    return jsonify(tx.to_dict()), 200


@transactions_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    data = request.get_json() or {}
    tx, error, status = create_transaction_for_user(user, data)
    if error:
        return jsonify({'message': error}), status
    return jsonify(tx.to_dict()), 201


@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    data = request.get_json() or {}
    tx, error, status = update_transaction_for_user(user, transaction_id, data)
    if error:
        return jsonify({'message': error}), status
    return jsonify(tx.to_dict()), 200


@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    identity = get_jwt_identity()
    user = User.query.get(identity['id'])
    error, status = delete_transaction_for_user(user, transaction_id)
    if error:
        return jsonify({'message': error}), status
    return jsonify({'message': 'Transaction deleted'}), 200
