from typeseam.app import db
from tests.test_base import BaseTestCase

from tests.mock.factories import SubmissionFactory

from typeseam.form_filler import models

sample_events = [{
      "by": "Louise.Winterstein@sfgov.org",
      "time": 1462924218.59,
      "key": "348720c41d218296bc96453bc35bc80a",
      "type": "opened"
    },
    {
      "by": "Louise.Winterstein@sfgov.org",
      "time": 1462924207.933,
      "key": "ae8be706a1093a1e9e49d98c069d722e",
      "type": "opened"
    },
    {
      "by": "Louise.Winterstein@sfgov.org",
      "time": 1462924192.199,
      "key": "525b9a7bb0b84c549123a015ea9d8044",
      "type": "opened"
    }]

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

    def test_logentry_from_event(self):
        event = models.LogEntry.from_parsed_front_event(sample_events[0])
        db.session.add(event)
        db.session.commit()







