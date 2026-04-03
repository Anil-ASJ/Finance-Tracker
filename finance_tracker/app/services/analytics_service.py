from collections import defaultdict
from datetime import datetime

from sqlalchemy import case, func

from ..models.transaction import Transaction


def _query_for_user(user):
    from .transaction_service import _base_query_for_user

    return _base_query_for_user(user)


def get_summary(user, start_date=None, end_date=None):
    query = _query_for_user(user)

    if start_date:
        query = query.filter(Transaction.date >= datetime.fromisoformat(start_date).date())
    if end_date:
        query = query.filter(Transaction.date <= datetime.fromisoformat(end_date).date())

    total_income = query.with_entities(func.coalesce(func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)), 0)).scalar() or 0
    total_expenses = query.with_entities(func.coalesce(func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)), 0)).scalar() or 0
    count = query.count()

    current_balance = float(total_income) - float(total_expenses)

    return {
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'current_balance': current_balance,
        'transaction_count': count,
    }


def get_category_breakdown(user, tx_type=None):
    query = _query_for_user(user)
    if tx_type:
        query = query.filter(Transaction.type == tx_type)

    rows = (
        query.with_entities(Transaction.category, func.sum(Transaction.amount))
        .group_by(Transaction.category)
        .all()
    )
    return {cat: float(total) for cat, total in rows}


def get_monthly_summary(user, year):
    query = _query_for_user(user)
    if year:
        query = query.filter(func.extract('year', Transaction.date) == year)

    rows = (
        query.with_entities(
            func.extract('month', Transaction.date).label('month'),
            func.sum(case((Transaction.type == 'income', Transaction.amount), else_=0)).label('income'),
            func.sum(case((Transaction.type == 'expense', Transaction.amount), else_=0)).label('expenses'),
        )
        .group_by('month')
        .order_by('month')
        .all()
    )

    result = []
    for month, income, expenses in rows:
        result.append({
            'month': int(month),
            'income': float(income or 0),
            'expenses': float(expenses or 0),
        })
    return result


def get_recent_activity(user, limit=10):
    query = _query_for_user(user)
    return query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).limit(limit).all()


def get_insights(user):
    summary = get_summary(user)
    breakdown = get_category_breakdown(user, tx_type='expense')

    insights = []
    if breakdown:
        max_cat = max(breakdown, key=breakdown.get)
        insights.append(f'Highest expense category: {max_cat} ({breakdown[max_cat]:.2f})')

    if summary['total_income']:
        savings_rate = (summary['current_balance'] / summary['total_income']) * 100
        insights.append(f'Estimated savings rate: {savings_rate:.1f}%')

    return insights
