from flask import Flask
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from api.config import Config

api_fairy = APIFairy()
db = SQLAlchemy()
ma = Marshmallow()
cors = CORS()
migrate = Migrate()


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    initialize_extensions(app)
    register_blueprints(app)
    return app


def initialize_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    if app.config.get("USE_CORS"):
        cors.init_app(app)
    api_fairy.init_app(app)


def register_blueprints(app):
    from api.auth import auth
    from api.user import user
    from api.bond import bond
    from api.commands import commands

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(commands)
    app.register_blueprint(bond)
