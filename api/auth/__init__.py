from flask import Blueprint

user = Blueprint("auth", __name__)

from api.auth import routes, schema