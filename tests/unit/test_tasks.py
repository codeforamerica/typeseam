from unittest import TestCase
from unittest.mock import Mock, patch
from typeseam.form_filler import tasks

class TestQueries(TestCase):

    @patch('typeseam.form_filler.tasks.request')
    @patch('typeseam.form_filler.tasks.sendgrid')
    @patch('typeseam.form_filler.tasks.sg')
    @patch('typeseam.form_filler.tasks.app')
    def test_send_submission_notification(self, app, sg, sendgrid, request):
        app.config = {
            'DEFAULT_ADMIN_EMAIL': 'me'
        }
        body = "\nReceived a new submission, 10, with 14 answers to 27 questions."
        submission = Mock(id=10)
        request.url = "https://localtesting:80/yolo"
        message = Mock()
        submission.answers.keys.return_value = range(27)
        submission.answers.items.return_value = [
            (n, '' if n % 2 else 1)
            for n in range(27)
        ] # 14 answers
        fake_Mail = Mock()
        fake_Mail.return_value = message
        sendgrid.Mail = fake_Mail

        tasks.send_submission_notification(submission)
        fake_Mail.assert_called_once_with(
            subject="New submission to https://localtesting:80/yolo",
            to='me',
            text=body
            )
        sg.send.assert_called_once_with(message)