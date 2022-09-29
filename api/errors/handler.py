from werkzeug.exceptions import HTTPException, InternalServerError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from api.errors import error
from flask import current_app
from api import api_fairy


@error.app_errorhandler(HTTPException)
def http_error(error):
    return {
        'code': error.code,
        'message': error.name,
        'description': error.description
    }, error.code


@error.app_errorhandler(IntegrityError)
def sqla_integrity_error(error):
    return {
        'code': 400,
        'message': "Database integrity error",
        'description': str(error.orig)
    }, 400


@error.app_errorhandler(SQLAlchemyError)
def sqlalchemy_error(error):  # pragma: no cover
    if current_app.config['DEBUG'] is True:
        return {
            'code': InternalServerError.code,
            'message': 'Database error',
            'description': str(error),
        }, 500
    else:
        return {
            'code': InternalServerError.code,
            'message': InternalServerError().name,
            'description': InternalServerError.description,
        }, 500


@api_fairy.error_handler
def validation_error(code, messages):  # pragma: no cover
    return {
        'code': code,
        'message': 'Validation Error',
        'description': ('The server found one or more errors in the '
                        'information that you sent.'),
        'errors': messages,
    }, code
