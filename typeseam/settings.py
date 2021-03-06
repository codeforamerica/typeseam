# -*- coding: utf-8 -*-
import os

from .settings_auth import AuthConfig

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, os.pardir))

server_name = os.environ.get('SERVER_NAME')

class Config(AuthConfig):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TYPEFORM_API_KEY = os.environ.get('TYPEFORM_API_KEY')
    SEAMLESS_DOCS_API_KEY = os.environ.get('SEAMLESS_DOCS_API_KEY')
    SEAMLESS_DOCS_API_SECRET = os.environ.get('SEAMLESS_DOCS_API_SECRET')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    MAIN_INTAKE_EMAIL = os.environ.get('MAIN_INTAKE_EMAIL')
    DEFAULT_ADMIN_EMAIL = os.environ.get('DEFAULT_ADMIN_EMAIL')
    DEFAULT_NOTIFICATION_EMAIL = os.environ.get('DEFAULT_NOTIFICATION_EMAIL')
    if server_name:
        SERVER_NAME = server_name
    # use https for external links on heroku
    if 'DYNO' in os.environ:
        EXTERNAL_SCHEME = 'https'
    else:
        EXTERNAL_SCHEME = 'http'

class ProdConfig(Config):
    ENV = 'prod'
    DEBUG = False


class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True
    LOAD_FAKE_DATA = True


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    TESTING = True
    DEBUG = True
