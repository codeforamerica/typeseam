import sys
import logging

DEFAULT_LOGGING_FORMAT = '''
%(asctime)s %(levelname)s %(message)s'''

def register_logging(app, config_string):
    app.logger.removeHandler(app.logger.handlers[0])
    if 'prod' in config_string.lower():
        app.logger.setLevel(logging.INFO)
    else:
        app.logger.setLevel(logging.DEBUG)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(DEFAULT_LOGGING_FORMAT))
    app.logger.addHandler(stdout_handler)
    return None
