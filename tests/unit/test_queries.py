from unittest import TestCase
from unittest.mock import Mock, patch

from typeseam.form_filler.queries import (
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
    def test_create_typeform(self, commit, add, Typeform, query):
        user = Mock(id=1)
        # if the thing exists this does not update the record
        # if it does not exist,
        typeform = create_typeform(form_key='asdkjf',
            title="A typeform", user=user, translator={})
        self.assertEqual(typeform, "pancake")


