from typeseam.app import db
from tests.test_base import BaseTestCase

from tests.mock.factories import SubmissionFactory

class TestModels(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_submission_fill_pdf(self):
        s = SubmissionFactory.create()
        db.session.commit()
        result = s.fill_pdf('data/pdfs/CleanSlateSinglePage.pdf')
        self.assertEqual(type(result), bytes)