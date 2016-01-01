import os
from flask import current_app
from flask.signals import Namespace
import sendgrid

class SendEmailError(Exception):
    pass

class SendGridEmailer(object):

    def __init__(self, app=None):
        self.app = app
        self.config = dict(
            MAIL_DEFAULT_SENDER='',
            SENDGRID_API_KEY=''
            )
        self.set_config(app)

    def init_app(self, app):
        self.set_config(app)

    def set_config(self, app=None):
        if app:
            self.config_from_app(app)
        else:
            self.config_from_env()
        self.sg = sendgrid.SendGridClient(self.config.get('SENDGRID_API_KEY',''))

    def config_from_app(self, app):
        for key in self.config:
            if key in app.config:
                self.config[key] = app.config[key]
        self.app = app

    def config_from_env(self):
        for key in self.config:
            self.config[key] = os.environ.get(key, self.config[key])

    def send(self, message):
        if not message.from_email:
            message.set_from(self.config['MAIL_DEFAULT_SENDER'])

        # send signal
        email_dispatched.send(current_app._get_current_object(), message=message)

        if self.app and self.app.testing:
            return

        status, reason = self.sg.send(message)
        if status == 200:
            return status, reason
        else:
            raise SendEmailError('{}: {}'.format(status, message))

signals = Namespace()
email_dispatched = signals.signal("email-dispatched", doc="""
Signal sent when an email is dispatched. This signal will also be sent
in testing mode, even though the email will not actually be sent.
""")