# -*- coding: utf-8 -*-
import os
from tests.test_base import BaseTestCase

from nose.plugins.attrib import attr

@attr(selenium=True, speed="slow")
class SeleniumBaseTestCase(BaseTestCase):
    """A base test case for Selenium functional testing
    """
    baseURL = os.environ.get('BASE_URL', 'http://localhost:9000')
    emailBaseURL = os.environ.get('TEST_EMAIL_URL', '')
    screenshots_folder = os.environ.get('TEST_SCREENSHOTS_FOLDER', 'tests/screenshots')

    def wait(self, seconds=5):
        self.browser.implicitly_wait(seconds)

    def get(self, path):
        self.browser.get(self.baseURL + path)

    def get_email(self, path=''):
        self.browser.get(self.emailBaseURL + path)

    def xpath(self, xpath=''):
        return self.browser.find_element_by_xpath(xpath)

    def screenshot(self, image_name):
        path = os.path.join(self.screenshots_folder, image_name)
        self.browser.save_screenshot(path)

    def setUp(self):
        BaseTestCase.setUp(self)
        from selenium import webdriver
        self.browser = webdriver.Firefox()
        from selenium.webdriver.common.keys import Keys
        self.keys = Keys

    def tearDown(self):
        self.browser.close()
        self.browser.quit()
