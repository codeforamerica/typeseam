from marshmallow import Schema, fields, post_dump
from typeseam.app import ma
from typeseam.auth.models import (
    User,
    )


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

class UserSerializer(LookupMixin):

    lookup_fields = (
        'email',
        )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password'
            )