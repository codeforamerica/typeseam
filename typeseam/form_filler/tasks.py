import requests
import os
import time
from datetime import datetime
import sendgrid
from flask import abort, request, render_template, current_app as app
from flask.ext.login import current_user
from typeseam.app import db, sg
from typeseam.utils import seamless_auth
from typeseam.form_filler import queries, models, logs
from typeseam.form_filler.front import Front

from flask_mail import Message

front_app = Front(os.environ.get('FRONT_API_TOKEN'))

SEAMLESS_BASE_URL = 'https://cleanslate.seamlessdocs.com/api/'

class SeamlessDocsSubmissionError(Exception):
    pass

class SeamlessDocsPDFError(Exception):
    pass

def get_typeform_responses(form_key):
    template = 'https://api.typeform.com/v0/form/{}'
    url = template.format(form_key)
    args = {
        'key': os.environ.get('TYPEFORM_API_KEY', None),
        'completed': 'true'}
    response = requests.get(url, params=args)
    response.raise_for_status()
    data = response.json()
    logs.log_typeform_get("'{id}', {count} responses".format(
        id=form_key, count=data['stats']['responses']['showing']))
    return data


def get_seamless_doc_pdf(response_id, pdf_wait_time=10):
    response = queries.get_response_model(response_id)
    if not response.seamless_id:
        form_id = os.environ.get('DEFAULT_SEAMLESS_FORM_ID')
    else:
        form_id = queries.get_seamless_doc_key_for_response(response)
    submit_result = submit_answers_to_seamless_docs(form_id, response.answers)
    response.seamless_submission_id = submit_result['application_id']
    db.session.commit()
    # wait
    time.sleep(pdf_wait_time)
    response.pdf_url = retrieve_seamless_docs_pdf_url(response.seamless_submission_id)
    db.session.commit()
    form = queries.get_typeform(id=response.typeform_id)
    response_data = queries.response_serializer.dump(response).data
    return form, response_data


def send_submission_notification(submission):
    questions = len(submission.answers.keys())
    answers = sum([a not in ('', None) for q, a in submission.answers.items()])
    text = render_template('notification_email.txt', submission=submission)
    message = sendgrid.Mail(
        subject="New application to {} received {}".format(
            request.url,
            submission.get_local_date_received().strftime("%-m/%-d/%Y %-I:%M %p %Z")),
        to=app.config['DEFAULT_NOTIFICATION_EMAIL'],
        text=text)
    sg.send(message)


def send_submission_viewed_notification(submission):
    text = render_template('submission_viewed_email.txt',
        submission=submission,
        user=current_user)
    message = sendgrid.Mail(
        subject="Application {} viewed by {}".format(
            submission.uuid, current_user.email
            ),
        to=app.config['DEFAULT_NOTIFICATION_EMAIL'],
        text=text
        )
    sg.send(message)

def pull_new_front_events(latest=None):
    latest_time=None
    if latest:
        latest_time = latest.datetime.timestamp()
    return front_app.get_events(latest_time)


def submit_answers_to_seamless_docs(form_id, answers):
    submit_url = SEAMLESS_BASE_URL + 'form/{}/submit'.format(form_id)
    response = requests.post(
        submit_url, auth=seamless_auth.build_seamless_auth(),
        data=answers)
    response.raise_for_status()
    data = response.json()
    if 'application_id' not in data:
        raise SeamlessDocsSubmissionError(
            "{response_text}".format(response_text=response.text))
    logs.log_seamless_post("'{app_id}' submitted to '{form_id}'".format(
        form_id=form_id, app_id=data['application_id']))
    return data


def retrieve_seamless_docs_pdf_url(application_id):
    app_url = SEAMLESS_BASE_URL + 'application/{app_id}/update_pdf'.format(
        app_id=application_id)
    response = requests.get(
        app_url, auth=seamless_auth.build_seamless_auth())
    response.raise_for_status()
    data = response.json()
    if data and isinstance(data, list) and '.pdf' in data[0]:
        logs.log_seamless_get_pdf(
            "pdf retrieved for '{app_id}'".format(app_id=application_id))
        return data[0]
    elif isinstance(data, list) and not data:
        logs.log_seamless_pdf_missing(
            "pdf not found for '{app_id}'".format(app_id=application_id))
        abort(404)
    else:
        raise SeamlessDocsSubmissionError(
            "{response_text}".format(response_text=response.text))

