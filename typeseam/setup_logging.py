import sys
import logging

def register_logging(app, config_string):
    if 'prod' in config_string.lower():

        # for heroku, just send everything to the console (instead of a file)
        # and it will forward automatically to the logging service

        # disable the existing flask handler, we are replacing it with our own
        app.logger.removeHandler(app.logger.handlers[0])

        app.logger.setLevel(logging.DEBUG)
        stdout = logging.StreamHandler(sys.stdout)
        stdout.setFormatter(logging.Formatter('''

%(asctime)s
%(levelname)s in %(module)s [%(funcName)s] | [%(pathname)s:%(lineno)d]
%(message)s
--------------------------------------------------------------------------------
'''))
        app.logger.addHandler(stdout)

    else:
        # log to console for dev & testing
        app.logger.setLevel(logging.DEBUG)

    return None
