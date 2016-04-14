from sqlalchemy import desc, inspect, func
from sqlalchemy.orm import subqueryload
from flask import abort
from flask.ext.login import current_user

from typeseam.app import db
import io
import csv
from pprint import pprint

from .models import (
    TypeformResponse,
    Typeform, SeamlessDoc,
    FormSubmission
    )

from .serializers import (
    TypeformResponseSerializer,
    FlatResponseSerializer,
    TypeformSerializer,
    SerializationError,
    DeserializationError
    )


response_serializer = TypeformResponseSerializer()
flat_response_serializer = FlatResponseSerializer()
typeform_serializer = TypeformSerializer()

def save_new_form_submission(data, county="sanfrancisco"):
    submission = FormSubmission(
        answers=data,
        county=county,
        )
    db.session.add(submission)
    db.session.commit()

def save_new_typeform_data(data, typeform=None):
    if typeform:
        data['user_id'] = typeform.user_id
        data['typeform_id'] = typeform.id
        data['translator'] = typeform.translator
    models, errors = response_serializer.load(
        data, many=True, session=db.session)
    new_responses = []
    if errors:
        raise DeserializationError(str(errors))
    if not models:
        return []
    for m in models:
        if not inspect(m).persistent:
            db.session.add(m)
            new_responses.append(m)
    if new_responses and typeform:
        update_typeform_with_new_responses(typeform, new_responses)
    db.session.commit()


def update_typeform_with_new_responses(typeform, responses):
    latest_date = max(responses, key=lambda r: r.date_received).date_received
    typeform.latest_response = latest_date
    db.session.add(typeform)


def get_typeforms_for_user(user):
    q = db.session.query(Typeform).\
            options(subqueryload(Typeform.responses)).\
            filter(Typeform.user_id == user.id).\
            order_by(desc(Typeform.latest_response))
    return typeform_serializer.dump(q.all(), many=True).data


def get_responses_for_typeform(typeform_id):
    q = db.session.query(TypeformResponse).\
        filter(TypeformResponse.typeform_id == typeform_id).\
        order_by(desc(TypeformResponse.date_received))
    responses = q.all()
    responses_data = response_serializer.dump(responses, many=True).data
    return responses_data


def get_responses_csv(user, typeform_key):
    typeform = get_typeform(model=True, user_id=user.id, form_key=typeform_key)
    # get responses
    results = db.session.query(TypeformResponse, Typeform.form_key).\
            join(Typeform, TypeformResponse.typeform_id == Typeform.id).\
            filter(Typeform.user_id == user.id, Typeform.form_key == typeform_key).\
            order_by(desc(TypeformResponse.date_received)).all()
    # serialize them
    data = flat_response_serializer.dump(results, many=True).data
    if len(data) < 1:
        abort(404)
    # build csv
    keys = list(data[0].keys())
    keys.sort()
    with io.StringIO() as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=keys, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerows(data)
        return csvfile.getvalue()


def get_seamless_doc_key_for_response(response):
    return SeamlessDoc.query.get(response.seamless_id).seamless_key


def get_response_model(response_id):
    return TypeformResponse.query.get(int(response_id))


def get_response_detail(user, response_id):
    response = get_response_model(response_id)
    if user.id != response.user_id:
        abort(403)
    return response_serializer.dump(response).data


def get_response_count():
    return db.session.query(func.count(TypeformResponse.id)).scalar()


def create_typeform(form_key, title, user_id, translator, **kwargs):
    params = dict(form_key=form_key, title=title, user_id=user_id)
    if not all([form_key, title, user_id, translator]):
        raise TypeError(
            "Creating a new Typeform requires form_key, title, user_id, and translator arguments")
    typeform = db.session.query(Typeform).filter_by(**params).first()
    if not typeform:
        params.update(dict(translator=translator, **kwargs))
        typeform = Typeform(**params)
        db.session.add(typeform)
        db.session.commit()
    return typeform


def get_typeform(model=False, **kwargs):
    params = {k: v for k, v in kwargs.items() if v}
    if not params:
        abort(404)
    typeform = db.session.query(Typeform).filter_by(**params).first()
    if not typeform:
        abort(404)
    if model:
        return typeform
    return typeform_serializer.dump(typeform).data
