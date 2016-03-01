# -*- coding: utf-8 -*-
import random
import factory
from faker import Factory as FakerFactory
from ago import human

from factory.alchemy import SQLAlchemyModelFactory

from typeseam.app import db
from typeseam.form_filler.models import (
    Typeform, TypeformResponse, SeamlessDoc
    )
from typeseam.auth.models import User
from typeseam.auth.queries import create_user, hash_password
from typeseam.form_filler.serializers import TypeformResponseSerializer

faker = FakerFactory.create('en_US', includes=['tests.mock.typeform'])


def lazy(func):
    return factory.LazyAttribute(func)


def deferred(func, *args, **kwargs):
    def toss(obj):
        return func(*args, **kwargs)
    return factory.LazyAttribute(toss)


def typeform_key(*args):
    '''example: "o2RrmA"
    '''
    return faker.password(
        length=6,
        special_chars=False,
        )

def seamless_form_id(*args):
    '''example: "CO14950000011885231"
    '''
    return faker.numerify('CO1####000011######')

def seamless_application_id(*args):
    '''example: "AP14782000010904892"
    '''
    return faker.numerify('AP1####00001#######')

def recent_date(start_date='-8w'):
    # return a datetime within last 8 weeks
    return faker.date_time_between(start_date=start_date)


class SessionFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class TypeformFactory(SessionFactory):
    form_key = lazy(typeform_key)
    title = lazy(lambda x: faker.sentence(nb_words=4))
    added_on = deferred(recent_date)

    class Meta:
        model = Typeform


class SeamlessDocFactory(SessionFactory):
    seamless_key = lazy(seamless_form_id)
    class Meta:
        model = SeamlessDoc


class TypeformResponseFactory(SessionFactory):
    date_received = deferred(recent_date)
    answers = lazy(lambda x: faker.answers())
    seamless_submission_id = lazy(seamless_application_id)

    class Meta:
        model = TypeformResponse


class UserFactory(SessionFactory):
    id = factory.Sequence(lambda n: n)
    email = factory.Faker('free_email')
    confirmed_at = deferred(recent_date)

    class Meta:
        model = User


def user_data(**kwargs):
    d = {
        'email': faker.email(),
        'password': faker.password(),
        'confirmed_at': recent_date()
        }
    d.update(**kwargs)
    return d


def fake_typeform_responses(num_responses=1, start_date='-8w'):
    responses = []
    for n in range(num_responses):
        response = {
          'answers': faker.answers(),
          'metadata': {
            'date_submit': faker.date_time_between(
                start_date=start_date).strftime("%Y-%m-%d %H:%M:%S")
            }}
        responses.append(response)
    return {'responses': responses,
        'stats': {'responses': {'showing': num_responses}}}

def fake_translated_typeform_responses(count=1):
    raw_responses = fake_typeform_responses(count)
    deserializer = TypeformResponseSerializer()
    models, errors = deserializer.load(raw_responses, many=True,
        session=db.session)
    if not errors:
        if count == 1:
            return models[0]
        else:
            return models

def generate_fake_responses(typeform=None, count=None, seamless_doc=None):
    deserializer = TypeformResponseSerializer()
    if count is None:
        count = random.randint(1, 20)
    raw_responses = fake_typeform_responses(count)
    models, errors = deserializer.load(
        raw_responses, many=True, session=db.session)
    if errors:
        print("!ERRORS generating fake responses!!:", errors)
    for m in models:
        if typeform:
            m.typeform_id = typeform.id
            if typeform.user_id:
                m.user_id = typeform.user_id
        if seamless_doc:
            m.seamless_id = seamless_doc.id
        db.session.add(m)
    if typeform:
        typeform.latest_response = max(
            models, key=lambda m: m.date_received
            ).date_received
        typeform.latest_response_relative = human(typeform.latest_response, precision=1)
        db.session.add(typeform)
    db.session.commit()
    return models


def generate_fake_typeforms(user=None, count=None):
    if count is None:
        count = random.randint(1, 6)
    forms = []
    user_id = None
    if user:
        user_id = user.id
    for i in range(count):
        form = TypeformFactory.create(
            user_id=user_id,
            added_on=recent_date(start_date=user.confirmed_at)
            )
        forms.append(form)
    db.session.commit()
    return forms

def generate_fake_seamlessdocs(user=None, count=None):
    if count is None:
        count = random.randint(1, 6)
    docs = []
    user_id = None
    if user:
        user_id = user.id
    for i in range(count):
        doc = SeamlessDocFactory.create(
            user_id=user_id,
            added_on=recent_date(start_date=user.confirmed_at)
            )
        docs.append(doc)
    db.session.commit()
    return docs

def fake_user_data(num_users=20):
    return [user_data() for n in range(num_users)]


def generate_fake_users(num_users=20):
    data = fake_user_data(num_users)
    users = []
    for datum in data:
        users.append(create_user(**datum))
    return users, data


def generate_fake_data(num_users=10):
    users, user_data = generate_fake_users(num_users)
    user_report = ""
    user_report += "\nCreated {} users:".format(num_users)
    user_report += '\n'.join([
        '    {email}: "{password}"'.format(**d)
        for d in user_data])
    form_sets = []
    doc_sets = []
    for user in users:
        form_sets.append(generate_fake_typeforms(user))
        doc_sets.append(generate_fake_seamlessdocs(user))
    response_sets = []
    for form_set, doc_set in zip(form_sets, doc_sets):
        for form in form_set:
            doc = random.choice(doc_set)
            response_sets.append(generate_fake_responses(form, None, doc))
    return user_report, user_data, users, form_sets, doc_sets, response_sets
