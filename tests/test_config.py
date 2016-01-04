# -*- coding: utf-8 -*-
import os
from typeseam.app import create_app
from typeseam.settings import ProdConfig, DevConfig


def test_production_config():
    os.environ['CONFIG'] = 'typeseam.settings.ProdConfig'
    app = create_app()
    assert app.config['ENV'] == 'prod'
    assert app.config['DEBUG'] is False


def test_dev_config():
    os.environ['CONFIG'] = 'typeseam.settings.DevConfig'
    app = create_app()
    assert app.config['ENV'] == 'dev'
    assert app.config['DEBUG'] is True
