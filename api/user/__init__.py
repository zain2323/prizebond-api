from flask import Blueprint

user = Blueprint("user", __name__)

from api.user import routes, schema
