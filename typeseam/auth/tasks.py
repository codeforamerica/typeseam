
import sendgrid
from flask import current_app, url_for
from typeseam.extensions import sg

class UserAlreadyRegisteredError(Exception):
    pass

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
    return sg.send(message)

def invite_new_user(email):
    user_manager = current_app.user_manager
    db_adapter = user_manager.db_adapter
    user, user_email = user_manager.find_user_by_email(email)
    if user:
        raise UserAlreadyRegisteredError('{} is already registered'.format(email))

    # the following is copied from flask_user.views.invite
    from flask_user import signals, emails
    user_invite = db_adapter.add_object(db_adapter.UserInvitationClass, email=email)
    db_adapter.commit()
    token = user_manager.generate_token(user_invite.id)
    accept_invite_link = url_for('user.register',
                                 token=token,
                                 _external=True)

    # Store token
    if hasattr(db_adapter.UserInvitationClass, 'token'):
        user_invite.token = token
        db_adapter.commit()
    try:
        # Send 'invite' email
        emails.send_invite_email(user_invite, accept_invite_link)
    except Exception as e:
        # delete new User object if send fails
        db_adapter.delete_object(user_invite)
        db_adapter.commit()
        raise

    signals \
        .user_sent_invitation \
        .send(current_app._get_current_object(), user_invite=user_invite)