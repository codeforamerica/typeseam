from unittest.mock import MagicMock, patch
from requests.exceptions import HTTPError
from werkzeug.exceptions import NotFound

from flask import current_app
from typeseam.app import load_initial_data

from typeseam.form_filler.tasks import (
    get_typeform_responses,
    get_seamless_doc_pdf,
    submit_answers_to_seamless_docs,
    retrieve_seamless_docs_pdf_url,
    SeamlessDocsSubmissionError
    )


from tests.test_base import BaseTestCase
from tests.mock.mock_api_responses import (
    FakeTypeformAPIResponses,
    FakeSeamlessDocsAPISubmitResponses,
    FakeSeamlessDocsAPIApplicationResponses
    )
from tests.mock.factories import (
    seamless_form_id,
    fake_translated_typeform_responses
    )

class TestExternalApiCalls(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        load_initial_data(current_app)
        self.answers = fake_translated_typeform_responses(1).answers
        self.form_key = 'o2RrmA'
        self.doc_id = 'CO14950000011885231'
        self.app_id = 'AP14782000010904892'

    @patch('typeseam.form_filler.tasks.requests')
    def test_typeform_success(self, mock_requests):
        # make sure that success is appropriately logged.
        mock_requests.get.return_value = FakeTypeformAPIResponses.OK
        with self.assertLogs( current_app.logger, level='INFO' ) as context_manager:
            get_typeform_responses(self.form_key)
            self.assertTrue(mock_requests.get.called)
            self.assertTrue(FakeTypeformAPIResponses.OK.json.called)
        self.assertIn('TYPEFORM_GET_RESPONSES', context_manager.output[0])
        self.assertIn('2 responses', context_manager.output[0])

    @patch('typeseam.form_filler.tasks.requests')
    def test_typeform_failures(self, mock_requests):
        # make sure that any non-ok responses raise and log HTTP Errors
        mock_requests.get.return_value = FakeTypeformAPIResponses.ERROR
        with self.assertRaises(HTTPError):
            with self.assertLogs( current_app.logger, level='ERROR') as context_manager:
                get_typeform_responses(self.form_key)
        mock_requests.get.return_value = FakeTypeformAPIResponses.NOT_FOUND
        with self.assertRaises(HTTPError):
            with self.assertLogs( current_app.logger, level='ERROR') as context_manager:
                get_typeform_responses(self.form_key)
        mock_requests.get.return_value = FakeTypeformAPIResponses.FORBIDDEN
        with self.assertRaises(HTTPError):
            with self.assertLogs( current_app.logger, level='ERROR') as context_manager:
                get_typeform_responses(self.form_key)

    @patch('typeseam.form_filler.tasks.requests')
    def test_seamless_submit_success(self, mock_requests):
        mock_requests.post.return_value = FakeSeamlessDocsAPISubmitResponses.OK
        with self.assertLogs( current_app.logger, level='INFO' ) as context_manager:
            result = submit_answers_to_seamless_docs(self.doc_id, self.answers)
        self.assertIn('SEAMLESS_POST_RESPONSE', context_manager.output[0])
        self.assertIn("submitted to '{}'".format(self.doc_id), context_manager.output[0])

    @patch('typeseam.form_filler.tasks.requests')
    def test_seamless_submit_http_errors(self, mock_requests):
        # HTTP Errors
        mock_requests.post.return_value = FakeSeamlessDocsAPISubmitResponses.ERROR
        with self.assertRaises(HTTPError):
            with self.assertLogs( current_app.logger, level='ERROR') as context_manager:
                submit_answers_to_seamless_docs(self.doc_id, self.answers)
        mock_requests.post.return_value = FakeSeamlessDocsAPISubmitResponses.NOT_FOUND
        with self.assertRaises(HTTPError):
            with self.assertLogs( current_app.logger, level='ERROR') as context_manager:
                submit_answers_to_seamless_docs(self.doc_id, self.answers)
        mock_requests.post.return_value = FakeSeamlessDocsAPISubmitResponses.FORBIDDEN
        with self.assertRaises(HTTPError):
            with self.assertLogs( current_app.logger, level='ERROR') as context_manager:
                submit_answers_to_seamless_docs(self.doc_id, self.answers)

    @patch('typeseam.form_filler.tasks.requests')
    def test_seamless_submit_misc_errors(self, mock_requests):
        # incorrect form id
        mock_requests.post.return_value = FakeSeamlessDocsAPISubmitResponses.MISSING_DOC
        with self.assertRaises(SeamlessDocsSubmissionError):
            with self.assertLogs( current_app.logger, level='ERROR') as context_manager:
                submit_answers_to_seamless_docs(self.doc_id, self.answers)

        # validation error
        mock_requests.post.return_value = FakeSeamlessDocsAPISubmitResponses.VALIDATION_ERROR
        with self.assertRaises(SeamlessDocsSubmissionError):
            with self.assertLogs( current_app.logger, level='ERROR') as context_manager:
                submit_answers_to_seamless_docs(self.doc_id, self.answers)

    @patch('typeseam.form_filler.tasks.requests')
    def test_seamless_pdf_success(self, mock_requests):
        mock_requests.get.return_value = FakeSeamlessDocsAPIApplicationResponses.OK
        with self.assertLogs( current_app.logger, level='INFO' ) as context_manager:
            result = retrieve_seamless_docs_pdf_url(self.app_id)
        self.assertIn('SEAMLESS_PDF_RESPONSE', context_manager.output[0])
        self.assertIn("pdf retrieved for '{}'".format(self.app_id), context_manager.output[0])

    @patch('typeseam.form_filler.tasks.requests')
    def test_seamless_pdf_missing(self, mock_requests):
        mock_requests.get.return_value = FakeSeamlessDocsAPIApplicationResponses.MISSING_PDF
        with self.assertRaises(NotFound):
            with self.assertLogs( current_app.logger, level='WARNING' ) as context_manager:
                result = retrieve_seamless_docs_pdf_url(self.app_id)
            self.assertIn("pdf not found for '{}'".format(self.app_id), context_manager.output[0])

    @patch('typeseam.form_filler.tasks.requests')
    def test_seamless_pdf_http_error(self, mock_requests):
        mock_requests.get.return_value = FakeSeamlessDocsAPIApplicationResponses.ERROR
        with self.assertRaises(HTTPError):
            with self.assertLogs( current_app.logger, level='ERROR' ) as context_manager:
                result = retrieve_seamless_docs_pdf_url(self.app_id)

