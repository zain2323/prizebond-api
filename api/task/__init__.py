from flask import Blueprint

task = Blueprint("task", __name__)

from api.task import tasks, routes
