from unittest.mock import patch
from tests.test_base import BaseTestCase
from werkzeug.exceptions import Unauthorized, Forbidden
import dateutil.parser
from ago import human

import csv
import io
from datetime import datetime

from tests.mock.factories import (
    generate_fake_users,
    generate_fake_typeforms,
    generate_fake_responses,
    SubmissionFactory,
    )

from typeseam.form_filler.serializers import (
    TypeformResponseSerializer,
    FlatResponseSerializer,
    TypeformSerializer,
    SerializationError,
    DeserializationError
    )

from typeseam.form_filler.queries import (
    db,
    get_response_model,
    save_new_typeform_data,
    get_typeforms_for_user,
    get_responses_for_typeform,
    get_responses_csv,
    get_response_model,
    get_response_detail,
    create_typeform,
    get_unopened_submissions,
    save_new_logentry
    )

response_serializer = TypeformResponseSerializer()
flat_response_serializer = FlatResponseSerializer()
typeform_serializer = TypeformSerializer()


def parse_csv(csv_string):
    data = []
    with io.StringIO(csv_string) as f:
        csv_reader = csv.DictReader(f)
        return [row for row in csv_reader]


class TestQueries(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        user = generate_fake_users(1)[0][0]
        typeforms = generate_fake_typeforms(user, 2)
        responses = generate_fake_responses(typeforms[0], 5)
        self.user = user
        self.typeforms = typeforms
        self.typeform = typeforms[0]
        self.responses = responses
        self.response = responses[0]

    def test_get_response_model(self):
        response = self.responses[0]
        result = get_response_model(str(response.id))
        self.assertEqual(response, result)

    def test_get_response_detail_success(self):
        response = self.responses[0]
        result = get_response_detail(
            self.user,
            response.id
        )
        serialized_response = response_serializer.dump(response).data
        self.assertDictEqual(serialized_response, result)

    def test_get_response_detail_abort(self):
        response = self.responses[0]
        other_user = generate_fake_users(1)[0][0]
        with self.assertRaises(Forbidden):
            result = get_response_detail(
                other_user,
                response.id
            )

    def test_get_responses_for_typeform(self):
        # make some other responses to see if they show up
        other_user = generate_fake_users(1)[0][0]
        other_typeform = generate_fake_typeforms(other_user, 1)[0]
        responses = get_responses_for_typeform(self.typeform.id)
        self.assertEqual(len(responses), 5)
        self.assertEqual(responses[0]['typeform_id'], self.typeform.id)
        responses = get_responses_for_typeform(other_typeform.id)
        self.assertEqual(len(responses), 0)

    def test_get_typeforms_for_user(self):
        forms = get_typeforms_for_user(self.user)
        self.assertEqual(len(forms), 2)
        # try a user with no forms
        other_user = generate_fake_users(1)[0][0]
        forms = get_typeforms_for_user(other_user)
        self.assertEqual(len(forms), 0)

    def test_get_responses_csv(self):
        csv_string = get_responses_csv(self.user, self.typeform.form_key)
        data = parse_csv(csv_string)
        self.assertEqual(len(data), 5)

    def test_create_typeform(self):
        # test simple creation case
        translator = {'field': ['other_field']}
        params = dict(
            form_key='di0sd7',
            title='A new typeform',
            user_id=self.user.id,
            translator=translator
            )
        typeform = create_typeform(**params)
        for key in params:
            self.assertEqual(getattr(typeform, key), params[key])


    def test_relative_dates(self):
        # generate some new data
        user = generate_fake_users(1)[0][0]
        typeforms = generate_fake_typeforms(user, 2)
        generate_fake_responses(typeforms[0], 10)
        # get forms and check the dates
        check_forms = get_typeforms_for_user(user)
        for form in check_forms:
            if form['response_count'] == 0:
                self.assertIsNone(form['latest_response'])
                self.assertEqual(form['latest_response_relative'], 'No responses yet')
            else:
                self.assertIsNotNone(form['latest_response'])
                check_date = dateutil.parser.parse(form['latest_response']).replace(tzinfo=None)
                self.assertEqual(human(check_date, precision=1), form['latest_response_relative'])
                check_responses = get_responses_for_typeform(form['id'])

        for response in check_responses:
            check_date = dateutil.parser.parse(response['date_received']).replace(tzinfo=None)
            self.assertEqual(human(check_date, precision=1), response['date_received_relative'])

    def test_get_unopened_submissions(self):
        # have two submissions
        submission_A = SubmissionFactory.create()
        submission_B = SubmissionFactory.create()
        db.session.commit()
        # one opened, one not opened
        from typeseam.form_filler.models import LogEntry
        log = LogEntry(
            datetime=datetime.now(),
            user='Louise.Winterstein@sfgov.org',
            submission_key=submission_A.uuid,
            event_type='opened',
            source='front'
            )
        db.session.add(log)
        db.session.commit()
        # # get unopened submissions
        unopened = get_unopened_submissions()
        self.assertEqual(len(unopened), 1)
        self.assertEqual(unopened[0], submission_B)




