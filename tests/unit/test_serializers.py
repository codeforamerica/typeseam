from unittest import TestCase, mock
from typeseam.form_filler.serializers import (
    TypeformResponseSerializer,
    FlatResponseSerializer,
    TypeformSerializer
    )

from typeseam.form_filler import form_field_processors


class TestSerializers(TestCase):

    def setUp(self):
        self.tr_serializer = TypeformResponseSerializer()
        self.fr_serializer = FlatResponseSerializer()
        self.t_serializer = TypeformSerializer()

    @mock.patch('typeseam.form_filler.serializers.translate.translate_to_seamless')
    def test_typeform_response_serializer_preload_parsing(self, translate_to_seamless):
        # this takes data and should return
        data = {
            'user_id': 1,
            'typeform_id': 1,
            'translator': {'cheese':'shop'},
            'responses': [
                {
                'metadata': {'date_submit': '2025-12-25'},
                'answers': {
                    'foo': 'bar'
                    }
                }
            ]
        }
        translated_answers = {'bar': 'foo'}
        translate_to_seamless.return_value = translated_answers
        expected_results = dict(
            user_id=1,
            typeform_id=1,
            answers=translated_answers,
            answers_translated=True,
            date_received='2025-12-25'
            )
        results = self.tr_serializer.parse_typeform_responses(data)
        translate_to_seamless.assert_called_with(data['responses'][0],
            data['translator'], processors=form_field_processors.lookup)
        self.assertDictEqual(results[0], expected_results)
