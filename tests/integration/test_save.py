from typeseam.app import db
from nose.plugins.attrib import attr
from tests.test_base import BaseTestCase

from tests.mock.factories import (
    generate_fake_data,
    generate_fake_users,
    generate_fake_typeforms,
    generate_fake_responses,
    SessionFactory,
    SubmissionFactory,
    UserFactory,
    TypeformFactory,
    SeamlessDocFactory,
    TypeformResponseFactory,
    User,
    Typeform, TypeformResponse, SeamlessDoc
    )


class TestSave(BaseTestCase):

    def test_save_a_user(self):
        generate_fake_users(1)
        users = User.query.all()
        self.assertEqual(len(users), 1)
        self.assertTrue(users[0].id)

    def test_save_a_typeform(self):
        form = TypeformFactory.create()
        forms = Typeform.query.all()
        self.assertEqual(len(forms), 1)
        self.assertTrue(forms[0].id)

    def test_save_a_seamless_doc(self):
        doc = SeamlessDocFactory.create()
        docs = SeamlessDoc.query.all()
        self.assertEqual(len(docs), 1)
        self.assertTrue(docs[0].id)

    def test_save_a_response(self):
        response = generate_fake_responses(None, 1)[0]
        responses = TypeformResponse.query.all()
        self.assertEqual(len(responses), 1)
        self.assertTrue(responses[0].id)

    def test_save_submission(self):
        s = SubmissionFactory.create()
        db.session.commit()
        self.assertEqual(len(s.uuid), 32)
        self.assertEqual(type(s.uuid), str)
        self.assertEqual(s.county, 'sanfrancisco')
        self.assertTrue(getattr(s, 'id'))
        self.assertTrue(getattr(s, 'date_received'))
        self.assertTrue(getattr(s, 'answers'))

    @attr(speed="slow")
    def test_save_everything(self):
        data = generate_fake_data(num_users=10)
        user_report, user_data, users, form_sets, doc_sets, response_sets = data
        users = User.query.all()
        forms = Typeform.query.all()
        docs = SeamlessDoc.query.all()
        responses = TypeformResponse.query.all()
        self.assertTrue(len(users) == 10)
        self.assertTrue(len(forms) > 0)
        self.assertTrue(len(docs) > 0)
        self.assertTrue(len(responses) > 0)
