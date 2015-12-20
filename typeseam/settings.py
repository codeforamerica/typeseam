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

class ProdConfig(Config):
    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

class DevConfig(Config):
    ENV = 'dev'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:////tmp/test.db')

class TestConfig(Config):
    TESTING = True
    DEBUG = True