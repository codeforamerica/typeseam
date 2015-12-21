from sqlalchemy import desc, inspect

from typeseam.app import db
from typeseam import utils

import io
import csv
from pprint import pprint

from .models import (
    TypeformResponse,
    Typeform
    )

from .serializers import (
    TypeformResponseModelSerializer,
    FlatResponseSerializer,
    TypeformSerializer
    )

from typeseam.intake import form_field_processors

response_serializer = TypeformResponseModelSerializer()
flat_response_serializer = FlatResponseSerializer()
form_serializer = TypeformSerializer()

def get_response_model(response_id):
    return TypeformResponse.query.get(int(response_id))

def get_response_detail(response_id):
    response = get_response_model(response_id)
    return response_serializer.dump(response).data

def most_recent_responses(count=20):
    q = TypeformResponse.query.\
            order_by(desc(TypeformResponse.date_received)).\
            limit(count)
    return response_serializer.dump(q.all(), many=True).data

def get_responses_csv():
    q = TypeformResponse.query.\
            order_by(desc(TypeformResponse.date_received)).all()
    data = flat_response_serializer.dump(q, many=True).data
    keys = list(data[0].keys())
    keys.sort()
    with io.StringIO() as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerows(data)
        return csvfile.getvalue()

def parse_typeform_data(data):
    items = []
    for response in data['responses']:
        translated_answers = utils.translate_to_seamless(response, processors=form_field_processors)
        items.append(dict(
            answers=translated_answers,
            answers_translated=True,
            date_received=response['metadata']['date_submit']
            ))
    models, errors = response_serializer.load(items, many=True, session=db.session)
    new_responses = []
    # if errors, report them
    for m in models or []:
        if not inspect(m).persistent:
            db.session.add(m)
            new_responses.append(m)
    db.session.commit()
    return response_serializer.dump(new_responses, many=True).data


