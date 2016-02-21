from unittest import mock
from tests.mock.factories import (
    fake_typeform_responses,
    seamless_form_id,
    seamless_application_id
    )
from requests import Response


def generate_fake_requests_response(status_code=200, json=None, **kwargs):
    props = {
        'status_code': status_code,
        'json.return_value': json
        }
    props.update(kwargs)
    response = mock.Mock(**props)
    response.raise_for_status = lambda: Response.raise_for_status(response)
    return response


class FakeResponsesBase:
    """Each of these class attributes contain a Mock object
    that imitates a requests.Response object
    """
    OK = generate_fake_requests_response(200)
    ERROR = generate_fake_requests_response(500)
    NOT_FOUND = generate_fake_requests_response(404)
    FORBIDDEN = generate_fake_requests_response(403)


class FakeTypeformAPIResponses(FakeResponsesBase):

    OK = generate_fake_requests_response(
        json=dict(http_status=200, **fake_typeform_responses(2))
        )

class FakeSeamlessDocsAPISubmitResponses(FakeResponsesBase):

    OK = generate_fake_requests_response(
        json={
            'result': True,
            'description': 'Submission successful',
            'application_id': seamless_application_id()
            }
        )

    MISSING_DOC = generate_fake_requests_response(
        status_code=200, json={
            "error": True,
            "error_log": [
                {
                    "error_code": "form_init_error",
                    "error_message": "Form '{}' not found".format(seamless_form_id())
                }
            ]
        }
        )

    VALIDATION_ERROR = generate_fake_requests_response(
        status_code=200, json={
        "result": False,
        "error_log": [
            {
                "error_code": "validation_fail",
                "error_message": "Validation failed on element 'Email Input' ['email_input']: Null value is given for a required field",
                "error_description": "submission:validate_submission"
            }
        ]})

class FakeSeamlessDocsAPIApplicationResponses(FakeResponsesBase):

    OK = generate_fake_requests_response(200,
        json=['https://somewhere.com/somepdf.pdf'])

    MISSING_PDF = generate_fake_requests_response(200,
        json=[])


