import os
from pprint import pprint
from nose.plugins.attrib import attr

from tests.test_base import SeleniumBaseTestCase

class TestAuthTasks(SeleniumBaseTestCase):

    user = {
        'email': os.environ.get('DEFAULT_USER_EMAIL', 'the_colonel@gmail.com'),
        'password': os.environ.get('DEFAULT_USER_PASSWORD', 'this-sketch-is-too-silly'),
    }

    def test_get_login_page(self):
        self.get('/login')
        self.assertIn('Log in', self.browser.title)
        self.screenshot('login.png')

    def test_able_to_login(self):
        self.get('/login')
        email_input = self.browser.find_element_by_name('email')
        email_input.send_keys(self.user['email'])
        password_input = self.browser.find_element_by_name('password')
        password_input.send_keys(self.user['password'])
        self.screenshot('login-filled.png')
        password_input.submit()

