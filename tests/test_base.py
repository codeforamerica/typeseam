# -*- coding: utf-8 -*-
import os
from flask.ext.testing import TestCase as FlaskTestCase

from typeseam.app import (
    create_app as _create_app,
    db
    )

from tests.utils import get_value_for_name

class BaseTestCase(FlaskTestCase):
    '''
    A base test case that boots our app
    '''
    def create_app(self):
        os.environ['CONFIG'] = 'typeseam.settings.TestConfig'
        app = _create_app()
        app.testing = True
        return app

    def get_input_value(self, name, response):
        return get_value_for_name(name, response.data.decode('utf-8'))

    def setUp(self):
        FlaskTestCase.setUp(self)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.get_engine(self.app).dispose()
