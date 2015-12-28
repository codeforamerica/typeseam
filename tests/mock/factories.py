# -*- coding: utf-8 -*-

import datetime

import factory
from faker import Factory as FakerFactory

from factory.alchemy import SQLAlchemyModelFactory

from typeseam.app import db
from typeseam.intake.models import Typeform, TypeformResponse
from typeseam.auth.queries import create_user

faker = FakerFactory.create('en_US', includes=['tests.mock.typeform'])

def lazy(func):
    return factory.LazyAttribute(func)

def typeform_key(x):
    '''example: "o8MrpO"
    '''
    return faker.password(
        length=6,
        special_chars=False,
        )

def recent_date(*args, **kwargs):
    # return a datetime within last 8 weeks
    return faker.date_time_between(start_date='-8w')

def user_data(**kwargs):
    d = {
        'email': faker.email(),
        'password': faker.password()
        }
    d.update(**kwargs)
    return d

class SessionFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class TypeformFactory(SessionFactory):
    id = factory.Sequence(lambda n: n)
    form_key = lazy(typeform_key)
    title = lazy(lambda x: faker.sentence(nb_words=4))
    class Meta:
        model = Typeform


class TypeformResponseFactory(SessionFactory):
    id = factory.Sequence(lambda n: n)
    date_received = lazy(recent_date)
    answers = lazy(lambda x: faker.answers())

    class Meta:
        model = TypeformResponse


def fake_user_data(num_users=20):
    return [user_data() for n in range(num_users)]

def generate_fake_users(n=20):
    data = fake_user_data(n)
    users = []
    for datum in data:
        users.append(create_user(datum))
    return users

def generate_fake_typeforms(n=10, user=None):
    pass

def generate_fake_typeform_responses(n=20, typeform=None):
    pass
