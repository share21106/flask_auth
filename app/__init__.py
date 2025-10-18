from flask import Flask
from pymongo import MongoClient
from flask import g


def create_app(config=None):
    app = Flask(__name__)
    app.config.update({
        'MONGO_URI': 'mongodb://localhost:27017/flask_auth',
        'SECRET_KEY': 'change-me',
    })
    if config:
        app.config.update(config)

    @app.before_request
    def before_request():
        if not hasattr(g, 'mongo'):
            g.mongo = MongoClient(app.config['MONGO_URI'])
            g.db = g.mongo.get_default_database()

    @app.teardown_appcontext
    def teardown(exception):
        mongo = getattr(g, 'mongo', None)
        if mongo is not None:
            mongo.close()

    from .auth import bp as auth_bp
    from .main import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
