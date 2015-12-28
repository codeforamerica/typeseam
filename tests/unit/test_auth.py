from tests.test_base import BaseTestCase
from flask import url_for, render_template
from pprint import pprint

class TestAuthViews(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.client = self.app.test_client()

    def test_login_url_resolves_to_auth_login_view(self):
        self.assertEqual( url_for('auth.login'), '/login')

    def test_login_uses_expected_html(self):
        r = self.client.get('/login')
        expected_html = render_template('auth/login.html', page_title='Log in', next='/')
        self.assertEqual(r.data.decode(), expected_html)



