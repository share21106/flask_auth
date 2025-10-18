from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object('config.Config')

    mongo.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app
