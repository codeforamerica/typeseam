import subprocess

from tests.test_base import BaseTestCase
from typeseam.app import db
from typeseam.form_filler.models import TypeformResponse
from typeseam.auth.models import User


class TestScripts(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_add_user_with_responses(self):
        subprocess.call([
            'python',
            'typeseam/scripts/add_user_with_responses.py',
            'myemail@someplace.org',
            'p4ssw0rd'
            ])
        user = db.session.query(User).filter(User.email=='myemail@someplace.org').first()
        self.assertTrue(user)
        responses = db.session.query(TypeformResponse).all()
        self.assertEqual(len(responses), 20)

