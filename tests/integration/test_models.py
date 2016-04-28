from typeseam.app import db
from tests.test_base import BaseTestCase

from tests.mock.factories import SubmissionFactory

class TestModels(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_submission_fill_pdf(self):
        s = SubmissionFactory.create()
        db.session.commit()
        result = s.fill_pdf('clean_slate')
        self.assertEqual(type(result), bytes)

    def test_submission_contact_preferences(self):
        submission = SubmissionFactory.create()
        media = ["email", "sms", "voicemail", "snailmail"]
        nice_contacts = ['Voicemail', 'Text Message', 'Email', 'Paper mail']
        for medium in media:
            submission.answers['prefers_' + medium] = "yes"
        db.session.commit()
        results = submission.get_contact_preferences()
        for thing in nice_contacts:
            self.assertIn(thing, results)
