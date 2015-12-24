# -*- coding: utf-8 -*-

import os

from flask.ext.testing import TestCase as FlaskTestCase

from typeseam.app import (
    create_app as _create_app,
    db
    )


class BaseTestCase(FlaskTestCase):
    '''
    A base test case that boots our app
    '''
    def create_app(self):
        os.environ['CONFIG'] = 'typeseam.settings.TestConfig'
        return _create_app()

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.get_engine(self.app).dispose()