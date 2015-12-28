from marshmallow import Schema, fields, post_dump
from typeseam.app import ma
from typeseam.intake.models import (
    TypeformResponse,
    Typeform
    )

from typeseam.auth.serializers import LookupMixin

# '2015-12-19 00:19:43'
TYPEFORM_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class TypeformResponseModelSerializer(LookupMixin):
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

class FlatResponseSerializer(ma.ModelSchema):
    answers = fields.Dict()
    date_received = fields.DateTime(format=TYPEFORM_DATE_FORMAT)

    class Meta:
        model = TypeformResponse
        fields = (
            'id',
            'date_received',
            'answers',
            'pdf_url'
            )

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
            'title'
            )