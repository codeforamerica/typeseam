from flask import url_for, render_template
from sqlalchemy import func, distinct
from pprint import pprint

from typeseam.app import db
from typeseam.auth.models import User
from typeseam.auth.queries import create_user

from tests.test_base import BaseTestCase
from tests.mock.factories import generate_fake_users

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

    def test_can_save_new_users(self):
        users = generate_fake_users(20)
        self.assertIsInstance(users[0], User)
        # count all the uniqe user emails
        count = db.session.query(func.count(distinct(User.email))).first()[0]
        self.assertEqual(count, 20)

    def test_new_user_password_is_properly_encrypted(self):
        # check that the password was hashed with bcrypt
        raw_password = "hello"
        user = create_user(dict(email="something@gmail.com", password=raw_password))
        encoded_raw_password = raw_password.encode('utf-8')
        presumably_hashed_password = user.password.encode('utf-8')
        import bcrypt
        self.assertEqual(
            bcrypt.hashpw(encoded_raw_password, presumably_hashed_password),
            presumably_hashed_password)

    def test_unauthenticated_home_page_resolves_to_login_view(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 302) # is it a redirect?
        r = self.client.get('/', follow_redirects=True)
        self.assertIn('Log in', r.data.decode('utf-8')) # did it redirect to Log in?

    def test_login_form_includes_csrf_token(self):
        raise NotImplementedError
        # go to login page

    def test_login_fails_without_csrf(self):
        raise NotImplementedError

    def test_login_warns_about_http_and_links_to_https(self):
        raise NotImplementedError

    def test_login_has_forgot_password_link(self):
        raise NotImplementedError

    def test_successful_login_redirects_to_next_with_message(self):
        raise NotImplementedError

    def test_forgot_password_view_exists(self):
        raise NotImplementedError

    def test_forgot_password_post_sends_email(self):
        raise NotImplementedError

    def test_forgot_password_view_errors_on_unused_email(self):
        raise NotImplementedError

    def test_password_reset_email_contains_proper_link(self):
        raise NotImplementedError

    def test_password_reset_link_expires(self):
        raise NotImplementedError

    def test_password_reset_form_looks_sufficient(self):
        raise NotImplementedError

    def test_password_reset_has_csrf_and_https_warning(self):
        raise NotImplementedError

    def test_password_reset_fails_without_csrf(self):
        raise NotImplementedError

    def test_successful_password_reset_goes_to_next_with_message(self):
        raise NotImplementedError

