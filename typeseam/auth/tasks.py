
import sendgrid
from typeseam.extensions import sg


def sendgrid_email(recipients=None, subject=None, html_message=None, text_message=None, sender=None):
    """
    sendgrid.Mail Args:
            to: Recipient or list
            to_name: Recipient name
            from_email: Sender email
            from_name: Sender name
            subject: Email title
            text: Email body
            html: Email body
            bcc: Recipient or list
            reply_to: Reply address
            date: Set date
            headers: Set headers
            files: Attachments
    """
    message = sendgrid.Mail(
        to=recipients,
        subject=subject,
        html=html_message,
        text=text_message,
        from_email=sender
        )
    result = sg.send(message)
    print(result)