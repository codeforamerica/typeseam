# -*- coding: utf-8 -*-

import os

from flask.ext.testing import TestCase as FlaskTestCase
from nose.plugins.attrib import attr

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
        app = _create_app()
        app.testing = True
        return app

    def setUp(self):
        FlaskTestCase.setUp(self)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.get_engine(self.app).dispose()


@attr(selenium=True, speed="slow")
class SeleniumBaseTestCase(BaseTestCase):

    baseURL = os.environ.get('BASE_URL', 'http://localhost:9000')
    screenshots_folder = os.environ.get('TEST_SCREENSHOTS_FOLDER', 'tests/screenshots')

    def get(self, path):
        self.browser.get(self.baseURL + path)

    def screenshot(self, image_name):
        path = os.path.join(self.screenshots_folder, image_name)
        self.browser.save_screenshot(path)

    def setUp(self):
        BaseTestCase.setUp(self)
        from selenium import webdriver
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.close()
        self.browser.quit()
