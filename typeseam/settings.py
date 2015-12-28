# -*- coding: utf-8 -*-
import os

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, os.pardir))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TYPEFORM_API_KEY = os.environ.get('TYPEFORM_API_KEY')
    SEAMLESS_DOCS_API_KEY = os.environ.get('SEAMLESS_DOCS_API_KEY')
    SEAMLESS_DOCS_API_SECRET = os.environ.get('SEAMLESS_DOCS_API_SECRET')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    USER_UNAUTHENTICATED_ENDPOINT = 'auth.login'

class ProdConfig(Config):
    ENV = 'prod'
    DEBUG = False

class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
    TESTING = True
    DEBUG = True