from datetime import date

from app import create_app, db
from app.models.user import User
from app.models.transaction import Transaction


app = create_app()


with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('admin123')

    analyst = User(username='analyst', email='analyst@example.com', role='analyst')
    analyst.set_password('analyst123')

    viewer = User(username='viewer', email='viewer@example.com', role='viewer')
    viewer.set_password('viewer123')

    db.session.add_all([admin, analyst, viewer])
    db.session.commit()

    sample_transactions = [
        Transaction(amount=25000, type='income', category='Salary', date=date(2024, 1, 1), user_id=admin.id),
        Transaction(amount=1500.5, type='expense', category='Groceries', date=date(2024, 1, 5), user_id=admin.id),
        Transaction(amount=800, type='expense', category='Rent', date=date(2024, 1, 3), user_id=analyst.id),
        Transaction(amount=1200, type='income', category='Freelance', date=date(2024, 2, 10), user_id=analyst.id),
        Transaction(amount=300, type='expense', category='Entertainment', date=date(2024, 2, 14), user_id=viewer.id),
    ]

    db.session.add_all(sample_transactions)
    db.session.commit()

    print('Database seeded with sample users and transactions')
