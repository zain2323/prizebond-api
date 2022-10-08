from flask import Flask, redirect, url_for
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_admin import Admin
from flask_login import LoginManager
from flask_admin.base import AdminIndexView
from flask_socketio import SocketIO


api_fairy = APIFairy()
db = SQLAlchemy()
ma = Marshmallow()
cors = CORS()
migrate = Migrate()
admin_manager = Admin(name="FastBondAdmin")
login_manager = LoginManager()
login_manager.login_view = "admin.sign_in"
login_manager.login_message_category = "info"
socketIO = SocketIO(cors_allowed_origins="*")


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    initialize_extensions(app)
    register_blueprints(app)
    return app


def initialize_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    login_manager.init_app(app)
    if app.config.get("USE_CORS"):
        cors.init_app(app)
    api_fairy.init_app(app)
    socketIO.init_app(app)

    # Restricting the admin panel index route
    from flask_login import current_user

    class RestrictIndexView(AdminIndexView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.role.name == 'admin'

        def inaccessible_callback(self, name, **kwargs):
            # redirect to login page if user doesn't have access
            return redirect(url_for('web_admin.sign_in'))

    admin_manager.init_app(app, index_view=RestrictIndexView())


def register_blueprints(app):
    from api.auth import auth
    from api.user import user
    from api.bond import bond
    from api.commands import commands
    from api.webadmin import web_admin
    from api.errors import error

    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(commands)
    app.register_blueprint(bond)
    app.register_blueprint(web_admin, url_prefix="/admin")
    app.register_blueprint(error)
