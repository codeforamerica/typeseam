from unittest import TestCase
from unittest.mock import Mock, patch

from typeseam.form_filler.models import (
    Typeform,
    SeamlessDoc,
    TypeformResponse
    )


class TestModels(TestCase):

    def test_typeform(self):
        for att in ['id', 'live_url', 'edit_url', 'form_key',
            'title', 'translator', 'user_id', 'added_on', 'latest_response',
            'responses']:
            self.assertTrue(getattr(Typeform, att))
