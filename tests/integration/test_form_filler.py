from flask import url_for
from typeseam.auth.queries import create_user, get_user_by_email
from typeseam.app import db
from typeseam.form_filler.models import Typeform

from tests.test_base import BaseTestCase
from tests.mock.factories import generate_fake_typeforms, generate_fake_responses
from datetime import datetime
from bs4 import BeautifulSoup

class TestFormFillerViews(BaseTestCase):

    sample_user_data = dict(email="something@gmail.com", password="Hell0", confirmed_at=datetime(2015, 12, 19, 6, 48, 3))
    fake_response_count = 5

    def setUp(self):
        BaseTestCase.setUp(self)
        self.client = self.app.test_client()
        # create a user and some fake data
        test_user = create_user(**self.sample_user_data)
        fake_typeform = generate_fake_typeforms(test_user, 1)[0]
        generate_fake_responses(fake_typeform, self.fake_response_count)

    def login(self, **kwargs):
        login_data = dict(**self.sample_user_data)
        login_data.update(**kwargs)
        get_response = self.client.get(url_for('user.login'))
        csrf_token = self.get_input_value('csrf_token', get_response)
        return self.client.post(
            url_for('user.login'),
            data=dict(csrf_token=csrf_token, **login_data),
            follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('user.logout'), follow_redirects=True)

    def get_user(self):
        return get_user_by_email(self.sample_user_data['email'])



