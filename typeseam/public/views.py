
import os
from datetime import datetime
from pytz import timezone
from flask import render_template, url_for, current_app, request
from typeseam.public import blueprint
from twilio import twiml
import sendgrid
from typeseam.app import sg, csrf



@blueprint.route('/privacy/')
def privacy_policy():
    return render_template('privacy_policy.html')


@blueprint.route('/voicemail/', methods=['GET'])
def voicemail_response():
    response = twiml.Response()
    # get the static URL
    static_url = os.environ.get('STATIC_URL', current_app.static_url_path)
    greeting_path = os.path.join(static_url, 'voicemail/CMR_voicemail_greeting.mp3')
    handle_voicemail_url = url_for(
        'public.handle_voicemail_recording',
        _external=True,
        _scheme=current_app.config.get('EXTERNAL_SCHEME', 'https')
        )
    response.play(greeting_path)
    response.record(
        action=handle_voicemail_url,
        method='POST')
    return str(response)

@csrf.exempt
@blueprint.route('/record/', methods=['POST'])
def handle_voicemail_recording():
    recording_url = request.values.get("RecordingUrl", '')
    from_number = request.values.get("From", '')
    duration = request.values.get("RecordingDuration", '')
    time_received = timezone('GMT').localize(
        datetime.utcnow()).astimezone(timezone('US/Pacific'))
    text = "Listen to the recording at {}".format(recording_url)
    # get the recording, attach it to the email
    message = sendgrid.Mail(
        subject="New voicemail from {} received {}".format(
            from_number,
            time_received.strftime("%-m/%-d/%Y %-I:%M %p %Z")),
        to=current_app.config['DEFAULT_NOTIFICATION_EMAIL'],
        text=text)
    response = twiml.Response()
    return str(response)
