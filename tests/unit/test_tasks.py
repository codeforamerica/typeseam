from unittest import TestCase
from unittest.mock import Mock, patch
from typeseam.form_filler import tasks

class TestTasks(TestCase):

    @patch('typeseam.form_filler.tasks.render_template')
    @patch('typeseam.form_filler.tasks.request')
    @patch('typeseam.form_filler.tasks.sendgrid')
    @patch('typeseam.form_filler.tasks.sg')
    @patch('typeseam.form_filler.tasks.app')
    def test_send_submission_notification(self, app, sg, sendgrid, request, render_template):
        app.config = {
            'DEFAULT_ADMIN_EMAIL': 'me'
        }
        fake_rendered_template = Mock()
        render_template.return_value = fake_rendered_template
        submission = Mock(id=10, uuid='a uuid')
        request.url = "https://localtesting:80/yolo"
        message = Mock()
        submission.answers.keys.return_value = range(27)
        submission.answers.items.return_value = [
            (n, '' if n % 2 else 1)
            for n in range(27)
        ] # 14 answers
        fake_time = Mock(strftime=Mock(return_value='<nice time format>'))
        submission.get_local_date_received.return_value = fake_time
        fake_Mail = Mock()
        fake_Mail.return_value = message
        sendgrid.Mail = fake_Mail
        tasks.send_submission_notification(submission)
        fake_Mail.assert_called_once_with(
            subject="New application to https://localtesting:80/yolo received <nice time format>",
            to='me',
            text=fake_rendered_template
            )
        sg.send.assert_called_once_with(message)