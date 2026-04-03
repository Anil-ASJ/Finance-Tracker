from datetime import datetime
from sqlalchemy import and_

from .. import db
from ..models.transaction import Transaction


ROLE_ADMIN = 'admin'
ROLE_ANALYST = 'analyst'
ROLE_VIEWER = 'viewer'


def _base_query_for_user(user):
    if user.role in (ROLE_ADMIN, ROLE_ANALYST):
        return Transaction.query
    return Transaction.query.filter_by(user_id=user.id)


def get_transactions_for_user(user, filters, page, per_page):
    query = _base_query_for_user(user)

    conditions = []
    tx_type = filters.get('type')
    if tx_type:
        conditions.append(Transaction.type == tx_type)

    category = filters.get('category')
    if category:
        conditions.append(Transaction.category == category)

    start_date = filters.get('start_date')
    if start_date:
        conditions.append(Transaction.date >= datetime.fromisoformat(start_date).date())

    end_date = filters.get('end_date')
    if end_date:
        conditions.append(Transaction.date <= datetime.fromisoformat(end_date).date())

    min_amount = filters.get('min_amount')
    if min_amount is not None:
        conditions.append(Transaction.amount >= float(min_amount))

    max_amount = filters.get('max_amount')
    if max_amount is not None:
        conditions.append(Transaction.amount <= float(max_amount))

    if conditions:
        query = query.filter(and_(*conditions))

    pagination = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    meta = {
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
    }
    return pagination.items, meta


def get_transaction_for_user(user, transaction_id):
    query = _base_query_for_user(user)
    return query.filter_by(id=transaction_id).first()


def create_transaction_for_user(user, data):
    from ..utils.validators import validate_transaction_payload

    error = validate_transaction_payload(data, require_all=True)
    if error:
        return None, error, 400

    tx = Transaction(
        amount=data['amount'],
        type=data['type'],
        category=data['category'],
        date=datetime.fromisoformat(data['date']).date() if data.get('date') else datetime.utcnow().date(),
        description=data.get('description'),
        notes=data.get('notes'),
        user_id=user.id,
    )

    db.session.add(tx)
    db.session.commit()
    return tx, None, 201


def update_transaction_for_user(user, transaction_id, data):
    tx = get_transaction_for_user(user, transaction_id)
    if not tx:
        return None, 'Transaction not found', 404

    # Analysts can only modify their own transactions
    if user.role == ROLE_ANALYST and tx.user_id != user.id:
        return None, 'Analyst can only modify own transactions', 403

    from ..utils.validators import validate_transaction_payload

    error = validate_transaction_payload(data, require_all=False)
    if error:
        return None, error, 400

    if 'amount' in data:
        tx.amount = data['amount']
    if 'type' in data:
        tx.type = data['type']
    if 'category' in data:
        tx.category = data['category']
    if 'date' in data:
        tx.date = datetime.fromisoformat(data['date']).date()
    if 'description' in data:
        tx.description = data['description']
    if 'notes' in data:
        tx.notes = data['notes']

    db.session.commit()
    return tx, None, 200


def delete_transaction_for_user(user, transaction_id):
    tx = get_transaction_for_user(user, transaction_id)
    if not tx:
        return 'Transaction not found', 404

    if user.role != ROLE_ADMIN:
        return 'Only admin can delete transactions', 403

    db.session.delete(tx)
    db.session.commit()
    return None, 200
