from flask import Blueprint

bond = Blueprint("bond", __name__)

from api.bond import routes, schema
