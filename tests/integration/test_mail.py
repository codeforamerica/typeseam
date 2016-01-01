from tests.test_base import BaseTestCase
from typeseam.utils.sendgrid_mailer import email_dispatched
from typeseam.auth.tasks import sendgrid_email


class TestMail(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.body = """Hey there, this is an email message."""
        self.subject = "Hello from mail tests"

    def send_mail(self):
        sendgrid_email(
            subject="testing mail again",
            recipients=['benjamin.j.golder@gmail.com'],
            text_message="What is up?"
            )

    def test_can_send_mail(self):
        messages = []
        def fire(app, message, **extra):
            messages.append(message)
        email_dispatched.connect(fire)
        self.send_mail()
        self.assertEqual(len(messages), 1)