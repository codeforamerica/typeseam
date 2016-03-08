from unittest import TestCase
from unittest.mock import Mock, patch

from typeseam.form_filler.views import (
    index,
    responses,
    response_detail,
    responses_csv,
    remote_responses,
    fill_seamless_docs_pdf,
    )


class TestViews(TestCase):

    @patch('flask_user.decorators.current_user', is_authenticated=True)
    @patch('typeseam.form_filler.views.os.environ.get')
    @patch('typeseam.form_filler.views.current_user', id=1)
    @patch('typeseam.form_filler.views.queries.get_typeform',
        return_value=Mock(id=1))
    @patch('typeseam.form_filler.views.tasks.get_typeform_responses')
    @patch('typeseam.form_filler.views.queries.save_new_typeform_data')
    @patch('typeseam.form_filler.views.queries.get_responses_for_typeform')
    @patch('typeseam.form_filler.views.render_template')
    def test_remote_responses_expected(self, render, get_responses, save_data,
        pull_responses, get_typeform, user, env_get, curr_user):
        typeform_key = 'jns98s'
        result = remote_responses(typeform_key)
        env_get.assert_not_called()
        get_typeform.assert_called_once_with(
            form_key=typeform_key, user_id=1, model=True)
        pull_responses.assert_called_once_with('jns98s')
        save_data.assert_called_once()
        get_responses.assert_called_once_with(typeform_id=1)
        render.assert_called_once()

