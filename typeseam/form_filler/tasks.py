import requests
import os
import time
from pprint import pprint
from flask import abort
from typeseam.app import db
from typeseam.utils import seamless_auth
from typeseam.form_filler import queries


def get_typeform_responses(form_key=None):
    if not form_key:
        form_key = os.environ.get('DEFAULT_TYPEFORM_KEY')
    template = 'https://api.typeform.com/v0/form/{}'
    url = template.format(form_key)
    args = {
        'key': os.environ.get('TYPEFORM_API_KEY', None),
        'completed': 'true'}
    data = requests.get(url, params=args).json()
    responses = queries.save_new_typeform_data(data, form_key)
    return responses


def get_seamless_doc_pdf(response_id):
    response = queries.get_response_model(response_id)
    base_url = 'https://cleanslate.seamlessdocs.com/api/'
    if not response.seamless_id:
        form_id = os.environ.get('DEFAULT_SEAMLESS_FORM_ID')
    else:
        form_id = queries.get_seamless_doc_key_for_response(response)
    submit_url = base_url + 'form/{}/submit'.format(form_id)
    submit_result = requests.post(
        submit_url, auth=seamless_auth.build_seamless_auth(),
        data=response.answers).json()
    if 'application_id' in submit_result:
        response.seamless_submission_id = submit_result['application_id']
        db.session.commit()
    else:
        # these abort errors should be more specific
        abort(404)
    app_url = base_url + 'application/{}'.format(
        response.seamless_submission_id)
    # wait for the pdf to be generated
    time.sleep(10)
    app_result = requests.get(
        app_url, auth=seamless_auth.build_seamless_auth()).json()
    response.pdf_url = app_result.get('submission_pdf_url', '')
    if response.pdf_url:
        db.session.commit()
    else:
        abort(404)
    form = queries.get_typeform(id=response.typeform_id)
    response_data = queries.response_serializer.dump(response).data
    return form, response_data
