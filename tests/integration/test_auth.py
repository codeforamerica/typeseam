from flask import url_for, request, session
from flask.ext.login import current_user
from sqlalchemy import func, distinct
from pprint import pprint

from typeseam.app import db
from typeseam.auth.models import User
from typeseam.auth.queries import create_user, get_user_by_email

from tests.test_base import BaseTestCase


class TestAuthViews(BaseTestCase):

    sample_user_data = dict(
        email="something@gmail.com",
        password="Hell0"
        )

    def setUp(self):
        BaseTestCase.setUp(self)
        self.client = self.app.test_client()
        create_user(**self.sample_user_data)

    def get_user(self):
        return get_user_by_email(self.sample_user_data['email'])

    def test_wrong_password_returns_to_login(self):
        response = self.login(password="not hello")
        self.assertIn('Sign in', response.data.decode('utf-8'))
        self.assertFalse(current_user.is_authenticated)

    def login(self, **kwargs):
        login_data = dict(**self.sample_user_data)
        login_data.update(**kwargs)
        get_response = self.client.get('/', follow_redirects=True)
        csrf_token = self.get_input_value('csrf_token', get_response)
        return self.client.post(
            url_for('user.login'),
            data=dict(csrf_token=csrf_token, **login_data),
            follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('user.logout'), follow_redirects=True)

    def test_new_user_password_is_properly_encrypted(self):
        # check that the password was hashed with bcrypt
        raw_password = self.sample_user_data['password']
        user = self.get_user()
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
        self.assertIn('Sign in', r.data.decode('utf-8')) # did it redirect to Log in?

    def test_login_form_includes_csrf_token(self):
        r = self.client.get(url_for('user.login'))
        self.assertIn('csrf_token', r.data.decode('utf-8'))

    def test_can_login(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)

    def test_can_logout(self):
        self.login()
        response = self.logout()
        self.assertFalse(current_user.is_authenticated)

    def test_successful_login_has_message(self):
        response = self.login()
        self.assertIn('signed in successfully', response.data.decode('utf-8'))

    def test_login_fails_without_csrf(self):
        response = self.client.post(
            url_for('user.login'),
            data=dict(**self.sample_user_data),
            follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    # def test_login_warns_about_http_and_links_to_https(self):
    #     raise NotImplementedError

    # def test_login_has_forgot_password_link(self):
    #     raise NotImplementedError

    # def test_forgot_password_post_sends_email(self):
    #     raise NotImplementedError

    # def test_forgot_password_view_errors_on_unused_email(self):
    #     raise NotImplementedError

    # def test_password_reset_email_contains_proper_link(self):
    #     raise NotImplementedError

    # def test_password_reset_link_expires(self):
    #     raise NotImplementedError

    # def test_password_reset_form_looks_sufficient(self):
    #     raise NotImplementedError

    # def test_password_reset_has_csrf_and_https_warning(self):
    #     raise NotImplementedError

    # def test_password_reset_fails_without_csrf(self):
    #     raise NotImplementedError

    # def test_successful_password_reset_goes_to_next_with_message(self):
    #     raise NotImplementedError

