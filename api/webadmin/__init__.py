from flask import Blueprint

web_admin = Blueprint("web_admin", __name__)

from api.webadmin import routes, forms, admin
