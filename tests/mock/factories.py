# -*- coding: utf-8 -*-

import datetime

import factory
from faker import Factory as FakerFactory

from factory.alchemy import SQLAlchemyModelFactory

from typeseam.app import db
from typeseam.intake.models import Typeform, TypeformResponse

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


class SessionFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class TypeformFactory(SessionFactory):
    id = factory.Sequence(lambda n: n)
    form_key = lazy(typeform_key)
    title = lazy(lambda x: return faker.sentence(nb_words=4))
    class Meta:
        model = Typeform


class TypeformResponseFactory(SessionFactory):
    id = factory.Sequence(lambda n: n)
    date_received = lazy(recent_date)
    answers = lazy(faker.answers)

    class Meta:
        model = TypeformResponse
