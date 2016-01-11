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
        get_response = self.client.get('/', follow_redirects=True)
        csrf_token = self.get_input_value('csrf_token', get_response)
        return self.client.post(
            url_for('user.login'),
            data=dict(csrf_token=csrf_token, **login_data),
            follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('user.logout'), follow_redirects=True)

    def get_user(self):
        return get_user_by_email(self.sample_user_data['email'])

    def test_correct_response_count(self):
        ''' The correct number of responses are reported in the form table.
        '''
        # login and check the baseline response count
        response = self.login()
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        self.assertEqual(str(self.fake_response_count), soup.find("td", {"data-test-id": "typeform-response-count"}).text.strip())
        # create a new response
        fake_user = self.get_user()
        fake_typeform = db.session.query(Typeform).filter(Typeform.user_id == fake_user.id).first()
        generate_fake_responses(fake_typeform, 1)
        # reload the front page and check the new response count
        response = self.client.get('/', follow_redirects=True)
        new_response_count = self.fake_response_count + 1
        soup = BeautifulSoup(response.data, 'html.parser')
        self.assertEqual(str(new_response_count), soup.find("td", {"data-test-id": "typeform-response-count"}).text.strip())
