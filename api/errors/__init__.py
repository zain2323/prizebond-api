from flask import Blueprint

error = Blueprint("error", __name__)

from api.errors import handler
