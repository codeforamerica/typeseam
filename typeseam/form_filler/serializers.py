from marshmallow import Schema, fields, pre_dump, post_dump, pre_load

from typeseam.app import ma
from pprint import pprint

from typeseam.form_filler.models import (
    TypeformResponse,
    Typeform
    )

from typeseam.utils import translate
from typeseam.form_filler import form_field_processors

from typeseam.auth.serializers import LookupMixin

# '2015-12-19 00:19:43'
TYPEFORM_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class DeserializationError(Exception):
    pass


class SerializationError(Exception):
    pass


class TypeformResponseSerializer(LookupMixin):
    answers = fields.Dict()
    date_received = fields.DateTime(format=TYPEFORM_DATE_FORMAT)

    lookup_fields = (
        'date_received',
        )

    class Meta:
        model = TypeformResponse
        fields = (
            'id',
            'date_received',
            'answers',
            'answers_translated',
            'seamless_submitted',
            'pdf_url'
            )

    @pre_load(pass_many=True)
    def parse_typeform_responses(self, data, many=True):
        items = []
        for response in data['responses']:
            translated_answers = translate.translate_to_seamless(
                response, processors=form_field_processors)
            items.append(dict(
                answers=translated_answers,
                answers_translated=True,
                date_received=response['metadata']['date_submit']
                ))
        return items


class FlatResponseSerializer(ma.ModelSchema):
    answers = fields.Dict()
    date_received = fields.DateTime(format=TYPEFORM_DATE_FORMAT)
    typeform_key = fields.Str()

    class Meta:
        model = TypeformResponse
        fields = (
            'id',
            'date_received',
            'answers',
            'pdf_url',
            'typeform_key'
            )

    @pre_dump(pass_many=True)
    def parse_db_join(self, data, many=True):
        parsed_data = []
        for response, form_key in data:
            response.typeform_key = form_key
            parsed_data.append(response)
        return parsed_data

    @post_dump(pass_many=True)
    def flatten(self, data, many=True):
        for datum in data:
            datum.update(datum.pop("answers"))
        return data


class TypeformSerializer(LookupMixin):

    lookup_fields = (
        'form_key',
        )

    class Meta:
        model = Typeform
        fields = (
            'form_key',
            'id',
            'title',
            'response_count',
            'latest_response'
            )
