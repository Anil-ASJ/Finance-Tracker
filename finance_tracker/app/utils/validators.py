from datetime import datetime


ALLOWED_TYPES = {'income', 'expense'}


def validate_transaction_payload(data, require_all=True):
    if require_all:
        required = ['amount', 'type', 'category']
        missing = [f for f in required if f not in data]
        if missing:
            return f"Missing fields: {', '.join(missing)}"

    if 'amount' in data:
        try:
            float(data['amount'])
        except (TypeError, ValueError):
            return 'amount must be a number'

    if 'type' in data and data['type'] not in ALLOWED_TYPES:
        return "type must be 'income' or 'expense'"

    if 'date' in data:
        try:
            datetime.fromisoformat(data['date'])
        except Exception:
            return 'date must be in ISO format YYYY-MM-DD'

    return None
