from flask import Flask, url_for, redirect, request
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_migrate import Migrate
from api.config import Config
# from flask_admin import Admin
# from flask_login import LoginManager
# from flask_admin.base import AdminIndexView

api_fairy = APIFairy()
db = SQLAlchemy()
ma = Marshmallow()
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
migrate = Migrate()
# admin_manager = Admin()
# login_manager = LoginManager()
# login_manager.login_view = "admin.sign_in"
# login_manager.login_message_category = "info"

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    initialize_extensions(app)
    register_blueprints(app)
    return app

def initialize_extensions(app):
    api_fairy.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    # login_manager.init_app(app)

    # # Restricting the admin panel index route
    # from flask_login import current_user
    # class RestrictIndexView(AdminIndexView):
    #     def is_accessible(self):
    #         return current_user.is_authenticated and current_user.role.role_name == 'admin'
        
    #     def inaccessible_callback(self, name, **kwargs):
    #         # redirect to login page if user doesn't have access
    #         return redirect(url_for('web_admin.sign_in'))
    
    # admin_manager.init_app(app, index_view=RestrictIndexView())

def register_blueprints(app):
    from api.user import user
    app.register_blueprint(user)