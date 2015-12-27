from nose.plugins.attrib import attr
from tests.test_base import BaseTestCase

@attr(selenium=True, speed="slow")
class TestSelenium(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        from selenium import webdriver
        self.driver = webdriver

    def test_index_get(self):
        browser = self.driver.Firefox()
        browser.get('http://localhost:9000/')
        assert 'Clean Slate' in browser.title
        browser.quit()