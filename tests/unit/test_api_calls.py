from unittest.mock import MagicMock, patch

from flask import current_app
from typeseam.app import load_initial_data

from typeseam.form_filler.tasks import (
    get_typeform_responses,
    get_seamless_doc_pdf
    )


from tests.test_base import BaseTestCase
from tests.mock.mock_api_responses import (
    good_response,
    forbidden_response,
    bad_response
    )

class TestExternalApiCalls(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        load_initial_data(current_app)

    @patch('typeseam.form_filler.tasks.requests')
    def test_typeform_success(self, mock_requests):
        from typeseam.form_filler.tasks import get_typeform_responses
        mock_requests.get.return_value = good_response
        get_typeform_responses()
        self.assertTrue(mock_requests.get.called)
        self.assertTrue(good_response.json.called)
