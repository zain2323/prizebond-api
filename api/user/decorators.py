from functools import wraps
from flask import current_app as app
from werkzeug.exceptions import Forbidden


def confirm_email_required(token_auth):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = token_auth.current_user()
            if not user.confirmed:
                raise Forbidden(
                    description="""You need to confirm email before you can access the website functionality.""")
            return func()
        return wrapper
    return decorator


def production_mode(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if app.debug:
            pass
        else:
            func(*args, **kwargs)
    return wrapper
