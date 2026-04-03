from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify

from ..models.user import User


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user = User.query.get(identity['id'])
            if not user or user.role not in roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
