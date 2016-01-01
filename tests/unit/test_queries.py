from unittest.mock import patch
from tests.test_base import BaseTestCase
from werkzeug.exceptions import Unauthorized, Forbidden

from tests.mock.factories import (
    generate_fake_users,
    generate_fake_typeforms,
    generate_fake_responses
    )

from typeseam.form_filler.serializers import (
    TypeformResponseSerializer,
    FlatResponseSerializer,
    TypeformSerializer,
    SerializationError,
    DeserializationError
    )

from typeseam.form_filler.queries import (
    get_response_model,
    save_new_typeform_data,
    get_typeforms_for_user,
    get_responses_for_typeform,
    get_responses_csv,
    get_response_model,
    get_response_detail
    )

response_serializer = TypeformResponseSerializer()
flat_response_serializer = FlatResponseSerializer()
typeform_serializer = TypeformSerializer()

class TestQueries(BaseTestCase):


    def setUp(self):
        BaseTestCase.setUp(self)
        user = generate_fake_users(1)[0][0]
        typeforms = generate_fake_typeforms(user, 2)
        responses = generate_fake_responses(typeforms[0], 5)
        self.user = user
        self.typeforms = typeforms
        self.typeform = typeforms[0]
        self.responses = responses
        self.response = responses[0]

    def test_get_response_model(self):
        response = self.responses[0]
        result = get_response_model(str(response.id))
        self.assertEqual(response, result)

    def test_get_response_detail_success(self):
        response = self.responses[0]
        result = get_response_detail(
            self.user,
            response.id
        )
        serialized_response = response_serializer.dump(response).data
        self.assertDictEqual(serialized_response, result)

    def test_get_response_detail_abort(self):
        response = self.responses[0]
        other_user = generate_fake_users(1)[0][0]
        with self.assertRaises(Forbidden):
            result = get_response_detail(
                other_user,
                response.id
            )

    def test_get_responses_for_typeform(self):
        # make some other responses to see if they show up
        other_user = generate_fake_users(1)[0][0]
        other_typeform = generate_fake_typeforms(other_user, 1)[0]
        form, responses = get_responses_for_typeform(
            self.user,
            self.typeform.form_key)
        self.assertEqual(len(responses), 5)
        self.assertEqual(form['form_key'], self.typeform.form_key)
        form, responses = get_responses_for_typeform(
            other_user,
            other_typeform.form_key
            )
        self.assertEqual(len(responses), 0)

    def test_get_typeforms_for_user(self):
        forms = get_typeforms_for_user(self.user)
        self.assertEqual(len(forms), 2)
        # try a user with no forms
        other_user = generate_fake_users(1)[0][0]
        forms = get_typeforms_for_user(other_user)
        self.assertEqual(len(forms), 0)


