from unittest import TestCase
from unittest.mock import Mock, patch

from typeseam.app import (
    load_initial_data,
    )


class TestModels(TestCase):

    @patch('typeseam.app.os.environ.get')
    def test_load_initial_data(self, env_get):
        ctx = Mock(return_value=Mock(
            __exit__=Mock(),
            __enter__=Mock()))
        app = Mock(app_context=ctx)
        load_initial_data(app)