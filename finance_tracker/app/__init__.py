from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
from flask import jsonify

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_object='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)

    from .models import user, transaction

    from .routes.auth_routes import auth_bp
    from .routes.transaction_routes import transactions_bp
    from .routes.analytics_routes import analytics_bp
    from .routes.user_routes import users_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(users_bp, url_prefix='/api/users')

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return jsonify({
            'message': 'Finance Tracker API is running',
            'status': 'ok'
        })
    return app