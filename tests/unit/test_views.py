from unittest import TestCase
from unittest.mock import Mock, patch

from typeseam.form_filler.views import (
    index,
    county_application,
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

    @patch('typeseam.form_filler.views.get_response_date')
    @patch('typeseam.form_filler.views.render_template')
    @patch('typeseam.form_filler.views.queries.get_typeform')
    @patch('typeseam.form_filler.views.current_user')
    def test_county_application_page(self, current_user, get_typeform, render_template, get_resp_date):
        import os
        form_key = os.environ.get('DEFAULT_TYPEFORM_KEY', 'jd9s8d')
        current_user.is_authenticated = False
        get_typeform.return_value = 'Typeform model'
        county_application()
        get_resp_date.assert_not_called()
        get_typeform.assert_called_with(form_key=form_key)
        render_template.called_once_with(
            'county_application_form.html',
            form='Typeform model')

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


