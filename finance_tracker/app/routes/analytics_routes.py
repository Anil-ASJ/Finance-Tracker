from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models.user import User
from ..services.analytics_service import (
    get_summary,
    get_category_breakdown,
    get_monthly_summary,
    get_recent_activity,
    get_insights,
)


analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/summary', methods=['GET'])
@jwt_required()
def summary():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    data = get_summary(user, start_date, end_date)
    return jsonify({'summary': data}), 200


@analytics_bp.route('/category-breakdown', methods=['GET'])
@jwt_required()
def category_breakdown():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    tx_type = request.args.get('type')
    data = get_category_breakdown(user, tx_type)
    return jsonify({'breakdown': data}), 200


@analytics_bp.route('/monthly-summary', methods=['GET'])
@jwt_required()
def monthly_summary():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    year = request.args.get('year', type=int)
    data = get_monthly_summary(user, year)
    return jsonify({'monthly': data}), 200


@analytics_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
def recent_activity():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    limit = request.args.get('limit', default=10, type=int)
    data = get_recent_activity(user, limit)
    return jsonify({'items': [t.to_dict() for t in data]}), 200


@analytics_bp.route('/insights', methods=['GET'])
@jwt_required()
def insights():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    data = get_insights(user)
    return jsonify({'insights': data}), 200
