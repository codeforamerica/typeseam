from unittest import TestCase
from unittest.mock import Mock, patch

from typeseam.form_filler.queries import (
    save_new_form_submission,
    get_response_model,
    create_typeform,
    save_new_typeform_data,
    get_typeforms_for_user,
    get_responses_for_typeform,
    get_responses_csv,
    get_response_model,
    get_response_detail
    )

from typeseam.form_filler.serializers import DeserializationError

class TestQueries(TestCase):

    @patch('typeseam.form_filler.queries.response_serializer.load',
            return_value=([Mock()],[]))
    @patch('typeseam.form_filler.queries.inspect',
            return_value = Mock(persistent=True))
    @patch('typeseam.form_filler.queries.db.session')
    @patch('typeseam.form_filler.queries.update_typeform_with_new_responses')
    def test_save_new_typeform_data(self, update, session, inspect, load):
        data = {}
        typeform = Mock(user_id=1, id=1, translator={})
        save_new_typeform_data(data, typeform)
        load.assert_called_with({
            'user_id':1,
            'typeform_id':1,
            'translator': {}
            }, many=True, session=session)

    @patch('typeseam.form_filler.queries.db.session.query')
    @patch('typeseam.form_filler.queries.Typeform')
    @patch('typeseam.form_filler.queries.db.session.add')
    @patch('typeseam.form_filler.queries.db.session.commit')
    def test_create_new_typeform(self, commit, add, PatchedTypeform, query):
        user = Mock(id=1)
        translator = { 'field': ['other_field']}
        mock_typeform = Mock()
        PatchedTypeform.return_value = mock_typeform

        lookup_params = dict(form_key='asdkjf', title="A typeform", user_id=user.id)
        att_params = dict(translator=translator, **lookup_params)

        # handle new typeform
        config = {'filter_by.return_value.first.return_value': []}
        query_mock = Mock(**config)
        query.return_value = query_mock
        typeform = create_typeform(**att_params)
        PatchedTypeform.assert_called_with(**att_params)
        query_mock.filter_by.assert_called_with(**lookup_params)
        add.assert_called_with(mock_typeform)
        commit.assert_called_with()
        self.assertEqual(typeform, mock_typeform)

    @patch('typeseam.form_filler.queries.db.session.query')
    @patch('typeseam.form_filler.queries.Typeform')
    @patch('typeseam.form_filler.queries.db.session.add')
    @patch('typeseam.form_filler.queries.db.session.commit')
    def test_create_existing_typeform(self, commit, add, PatchedTypeform, query):
        user = Mock(id=1)
        translator = { 'field': ['other_field']}
        mock_typeform = Mock()

        lookup_params = dict(form_key='asdkjf', title="A typeform", user_id=user.id)
        att_params = dict(translator=translator, **lookup_params)

        # handle attempt to create an existing typeform
        config = {'filter_by.return_value.first.return_value': mock_typeform}
        query_mock = Mock(**config)
        query.return_value = query_mock
        typeform = create_typeform(**att_params)
        query_mock.filter_by.assert_called_with(**lookup_params)
        self.assertEqual(typeform, mock_typeform)
        PatchedTypeform.assert_not_called()
        add.assert_not_called()
        commit.assert_not_called()


    @patch('typeseam.form_filler.queries.FormSubmission')
    @patch('typeseam.form_filler.queries.db.session.commit')
    @patch('typeseam.form_filler.queries.db.session.add')
    def test_save_new_form_submission(self, add, commit, FormSubmission):
        fake_submission_instance = Mock()
        FormSubmission.return_value = fake_submission_instance
        mock_data = Mock()
        result = save_new_form_submission(mock_data)
        FormSubmission.assert_called_once_with(answers=mock_data, county="sanfrancisco")
        add.assert_called_once_with(fake_submission_instance)
        commit.assert_called_once_with()
        self.assertEqual(result, fake_submission_instance)





