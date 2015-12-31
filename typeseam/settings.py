# -*- coding: utf-8 -*-
import os

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, os.pardir))

from .settings_auth import AuthConfig

class Config(AuthConfig):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TYPEFORM_API_KEY = os.environ.get('TYPEFORM_API_KEY')
    SEAMLESS_DOCS_API_KEY = os.environ.get('SEAMLESS_DOCS_API_KEY')
    SEAMLESS_DOCS_API_SECRET = os.environ.get('SEAMLESS_DOCS_API_SECRET')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SERVER_NAME = os.environ.get('HOST_NAME', 'localhost:9000')

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