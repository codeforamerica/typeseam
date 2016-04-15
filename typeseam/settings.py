# -*- coding: utf-8 -*-
import os

from .settings_auth import AuthConfig

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, os.pardir))


class Config(AuthConfig):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TYPEFORM_API_KEY = os.environ.get('TYPEFORM_API_KEY')
    SEAMLESS_DOCS_API_KEY = os.environ.get('SEAMLESS_DOCS_API_KEY')
    SEAMLESS_DOCS_API_SECRET = os.environ.get('SEAMLESS_DOCS_API_SECRET')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    DEFAULT_ADMIN_EMAIL = os.environ.get('DEFAULT_ADMIN_EMAIL')


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
