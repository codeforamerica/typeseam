from marshmallow import Schema, fields
from typeseam.extensions import ma
from typeseam.intake.models import (
    TypeformResponse,
    Typeform
    )
# '2015-12-19 00:19:43'
TYPEFORM_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class LookupMixin(ma.ModelSchema):
    def get_instance(self, data):
        """Overrides ModelSchema.get_instance with custom lookup fields"""
        filters = {
            key: data[key]
            for key in self.fields.keys() if key in self.lookup_fields}

        if None not in filters.values():
            return self.session.query(
                self.opts.model
            ).filter_by(
                **filters
            ).first()
        return None

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