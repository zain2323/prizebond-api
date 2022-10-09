from functools import wraps
from flask import current_app as app
from werkzeug.exceptions import Forbidden


def confirm_email_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not args["user"].confirmed:
            raise Forbidden(
                description="""You need to confirm email before you can access
                                the website functionality.""")
        func(*args, **kwargs)
    return wrapper


def production_mode(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if app.debug:
            pass
        else:
            func(*args, **kwargs)
    return wrapper
