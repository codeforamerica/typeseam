
from tests.mock.factories import faker, fake_typeform_responses
from unittest.mock import MagicMock



good_response = MagicMock()
sample_response = fake_typeform_responses(2)
sample_response.update(http_status=200)
good_response.json.return_value = sample_response

forbidden_response = MagicMock()
forbidden_response.json.return_value = {
    'http_status': 403,
}

bad_response = MagicMock()
bad_response.json.return_value = {
    'http_status': 500,
}

