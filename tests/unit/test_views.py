from unittest import TestCase
from unittest.mock import Mock, patch

from typeseam.form_filler.views import (
    index,
    county_application,
    get_filled_pdf,
    responses,
    response_detail,
    responses_csv,
    remote_responses,
    fill_seamless_docs_pdf,
    get_response_date
    )


class TestViews(TestCase):

    @patch('flask_user.decorators.current_user', is_authenticated=True)
    @patch('typeseam.form_filler.views.os.environ.get')
    @patch('typeseam.form_filler.views.current_user', id=1)
    @patch('typeseam.form_filler.views.queries.get_typeform')
    @patch('typeseam.form_filler.views.tasks.get_typeform_responses')
    @patch('typeseam.form_filler.views.queries.save_new_typeform_data')
    @patch('typeseam.form_filler.views.queries.get_responses_for_typeform')
    @patch('typeseam.form_filler.views.render_template')
    def test_remote_responses_expected(self, render, get_responses, save_data,
        pull_responses, get_typeform, user, env_get, curr_user):
        typeform_key = 'jns98s'
        mock_typeform = Mock(id=1)
        get_typeform.return_value = mock_typeform
        mock_results = Mock()
        pull_responses.return_value = mock_results
        get_responses.return_value = "responses"
        result = remote_responses(typeform_key)
        env_get.assert_not_called()
        get_typeform.assert_called_once_with(
            form_key=typeform_key, user_id=1, model=True)
        pull_responses.assert_called_once_with('jns98s')
        save_data.assert_called_once_with(mock_results, mock_typeform)
        get_responses.assert_called_once_with(typeform_id=1)
        render.assert_called_once_with("response_list.html",
            form=mock_typeform, responses="responses")

    @patch('typeseam.form_filler.views.render_template')
    @patch('typeseam.form_filler.views.queries.get_typeforms_for_user')
    @patch('typeseam.form_filler.views.current_user')
    def test_index_authenticated(self, current_user, get_typeforms, render_template):
        current_user.is_authenticated = True
        get_typeforms.return_value = 'forms'
        index()
        get_typeforms.called_once_with(current_user)
        render_template.called_once_with('user_splash.html', typeforms='forms')

    @patch('typeseam.form_filler.views.get_response_date')
    @patch('typeseam.form_filler.views.render_template')
    @patch('typeseam.form_filler.views.queries.get_typeforms_for_user')
    @patch('typeseam.form_filler.views.current_user')
    def test_index_unauthenticated(self, current_user, get_typeforms,
            render_template, get_resp_date):
        current_user.is_authenticated = False
        get_resp_date.return_value = '4 weeks from now'
        index()
        get_typeforms.assert_not_called()
        get_resp_date.assert_called_once_with()
        render_template.called_once_with('main_splash.html',
            page_title='Clear My Record - Code for America',
            response_estimate='4 weeks from now')

    @patch('typeseam.form_filler.views.render_template')
    @patch('typeseam.form_filler.views.current_user')
    @patch('typeseam.form_filler.views.request')
    def test_get_county_application_page(self, request, current_user, render_template):
        request.method = 'GET'
        current_user.is_authenticated = False
        county_application()
        render_template.called_once_with(
            'county_application_form.html')

    @patch('typeseam.form_filler.views.tasks.send_submission_notification')
    @patch('typeseam.form_filler.views.queries.save_new_form_submission')
    @patch('typeseam.form_filler.views.redirect')
    @patch('typeseam.form_filler.views.url_for')
    @patch('typeseam.form_filler.views.current_user')
    @patch('typeseam.form_filler.views.request')
    def test_post_county_application_form(self, request, current_user, url_for, redirect,
            save_new_submission, send_notification):
        request.method = 'POST'
        fake_form_data = Mock()
        request.form.to_dict.return_value = fake_form_data
        current_user.is_authenticated = False
        url_for_result = Mock()
        url_for.return_value = url_for_result
        fake_submission = Mock()
        save_new_submission.return_value = fake_submission
        # run
        county_application()
        save_new_submission.assert_called_once_with(fake_form_data)
        send_notification.assert_called_once_with(fake_submission)
        redirect.assert_called_once_with(url_for_result)

    @patch('typeseam.form_filler.views.tasks.send_submission_viewed_notification')
    @patch('typeseam.form_filler.views.queries.get_submission_by_uuid')
    @patch('typeseam.form_filler.views.os.path.join')
    @patch('typeseam.form_filler.views.send_file')
    @patch('typeseam.form_filler.views.io')
    @patch('typeseam.form_filler.views.PROJECT_ROOT')
    @patch('flask_user.decorators.current_user', is_authenticated=True)
    def test_get_filled_pdf(self, current_user, PROJECT_ROOT, io, send_file, join, get_submission_by_uuid, 
            send_submission_viewed_notification):
        actual_pdf_path = 'data/pdfs/CleanSlateSinglePage.pdf'
        actual_mimetype = 'application/pdf'
        mock_pdf_path = Mock()
        mock_pdf = Mock()
        mock_submission = Mock()
        mock_fill = Mock(return_value=mock_pdf)
        mock_submission.fill_pdf = mock_fill
        mock_raw_pdf_data = Mock()
        mock_BytesIO = Mock(return_value=mock_raw_pdf_data)
        io.BytesIO = mock_BytesIO
        get_submission_by_uuid.return_value = mock_submission
        join.return_value = mock_pdf_path
        # run
        get_filled_pdf('uuid')
        get_submission_by_uuid.assert_called_once_with('uuid')
        join.assert_called_once_with(PROJECT_ROOT, actual_pdf_path)
        mock_fill.assert_called_once_with(mock_pdf_path)
        send_submission_viewed_notification.assert_called_once_with(mock_submission)
        mock_BytesIO.assert_called_once_with(mock_pdf)
        send_file.assert_called_once_with(
            mock_raw_pdf_data,
            mimetype=actual_mimetype
            )

    @patch('typeseam.form_filler.views.datetime')
    @patch('typeseam.form_filler.views.timedelta')
    def test_get_response_date(self, timedelta, datetime):
        now = Mock(return_value=1)
        datetime.now = now
        timedelta.return_value = 1
        result = get_response_date()
        self.assertEqual(result, 2)
        now.assert_called_once_with()
        timedelta.assert_called_once_with(days=28)


