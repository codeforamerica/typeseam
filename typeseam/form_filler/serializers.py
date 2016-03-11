from marshmallow import fields, pre_dump, post_dump, pre_load

from typeseam.app import ma
from datetime import datetime
from ago import human

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
    user_id = fields.Int(allow_none=True)
    typeform_id = fields.Int(allow_none=True)
    seamless_id = fields.Int(allow_none=True)
    answers = fields.Dict()
    date_received = fields.DateTime(format=TYPEFORM_DATE_FORMAT)

    lookup_fields = (
        'date_received',
        'typeform_id',
    )

    class Meta:
        model = TypeformResponse
        fields = (
            'id',
            'user_id',
            'typeform_id',
            'seamless_id',
            'date_received',
            'date_received_relative',
            'answers',
            'answers_translated',
            'seamless_submitted',
            'pdf_url'
        )

    @pre_load(pass_many=True)
    def parse_typeform_responses(self, data, many=True):
        items = []
        user_id = data.get('user_id', None)
        typeform_id = data.get('typeform_id', None)
        translator = data['translator']
        for response in data['responses']:
            translated_answers = translate.translate_to_seamless(
                response, translator, processors=form_field_processors.lookup)
            items.append(dict(
                user_id=user_id,
                typeform_id=typeform_id,
                answers=translated_answers,
                answers_translated=True,
                date_received=response['metadata']['date_submit']
            ))
        return items

    @pre_dump()
    def add_display_fields(self, data):
        # add a relative date received
        data.date_received_relative = human(data.date_received, precision=1)
        return data


class FlatResponseSerializer(ma.ModelSchema):
    answers = fields.Dict()
    date_received = fields.DateTime(format=TYPEFORM_DATE_FORMAT)
    typeform_key = fields.Str()

    class Meta:
        model = TypeformResponse
        fields = (
            'id',
            'date_received',
            'date_received_relative',
            'answers',
            'pdf_url',
            'typeform_key'
        )

    @pre_dump(pass_many=True)
    def parse_db_join(self, data, many=True):
        parsed_data = []
        for response, form_key in data:
            response.typeform_key = form_key
            response.date_received_relative = human(response.date_received, precision=1)
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
            'latest_response',
            'latest_response_relative',
            'live_url',
            'edit_url'
        )

    @pre_dump()
    def add_display_fields(self, data):
        # add a count of the number of responses
        data.response_count = len(data.responses)
        data.latest_response_relative = human(data.latest_response, precision=1) if data.response_count > 0 else 'No responses yet'
        return data
