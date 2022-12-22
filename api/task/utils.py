from werkzeug.exceptions import Forbidden
from flask import current_app as app


def confirm_email_required(token_auth):
    if not app.debug:
        user = token_auth.current_user()
        if not user.confirmed:
            raise Forbidden(
                description="""You need to confirm email before you can access the website functionality.""")