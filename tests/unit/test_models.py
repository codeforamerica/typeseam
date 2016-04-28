from unittest import TestCase
from unittest.mock import Mock, patch

from typeseam.form_filler.models import (
    Typeform,
    SeamlessDoc,
    TypeformResponse,
    FormSubmission,
    fmt_ssn
    )


class TestModels(TestCase):

    def test_typeform(self):
        for att in ['id', 'live_url', 'edit_url', 'form_key',
            'title', 'translator', 'user_id', 'added_on', 'latest_response',
            'responses']:
            self.assertTrue(getattr(Typeform, att))

    def test_ssn_fmt(self):
        inputs = [
            '000000000',
            '000-00-0000'
        ]
        for entry in inputs:
            fake_submission = Mock(answers={
                'ssn': entry
                })
            self.assertEqual(fmt_ssn(fake_submission), '000-00-0000')
        fake_submission = Mock(answers={
                'ssn': ''
                })
        self.assertEqual(fmt_ssn(fake_submission), '')

