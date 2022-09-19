import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


class Config:
    # API documentation
    APIFAIRY_TITLE = 'Prizebond API'
    APIFAIRY_VERSION = '1.0'
    APIFAIRY_UI = 'elements'

    # Flask Admin
    FLASK_ADMIN_SWATCH = 'cyborg'

    # Marshmallow
    JSON_SORT_KEYS = False

    # Flask options
    SECRET_KEY = os.getenv("SECRET_KEY", "topSecret!")
    UPLOAD_FOLDER = './api/static/user/avatars'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # email options
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or '25')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER',
                                         'donotreply@fastbond.example.com')

    # Token configuration
    ACCESS_TOKEN_MINUTES = int(os.environ.get('ACCESS_TOKEN_MINUTES') or '15')
    REFRESH_TOKEN_DAYS = int(os.environ.get('REFRESH_TOKEN_DAYS') or '7')

    # CORS
    USE_CORS = True
