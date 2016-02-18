from unittest import TestCase
import logging
from tests.test_base import BaseTestCase
from flask import current_app
from typeseam.setup_logging import DEFAULT_LOGGING_FORMAT

def restore_logging_format(logger):
    logger.handlers[0].setFormatter(logging.Formatter(DEFAULT_LOGGING_FORMAT))

class TestException(Exception):
    pass

class TestLogging(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_logs_errors_correctly(self):
        with self.assertRaises(TestException):
            with self.assertLogs( current_app.logger, level='ERROR' ) as context_manager:
                raise TestException("Hello errors")
            self.assertIn("Hello errors", context_manager.output)
            self.assertIn("ERROR", context_manager.output)

    def test_logs_events_correctly(self):
        logger = current_app.logger
        self.assertEqual(logger.handlers[0].formatter._fmt, DEFAULT_LOGGING_FORMAT)
        with self.assertLogs( logger, level='DEBUG' ) as context_manager:
            logger.info("Something noteable happened")
            logger.debug("Something happened that isn't very significant")
        self.assertIn("Something noteable happened", context_manager.output[0])
        self.assertIn("INFO", context_manager.output[0])
        self.assertIn("Something happened that isn't very significant", context_manager.output[1])
        self.assertIn("DEBUG", context_manager.output[1])