
import os
from flask import render_template, jsonify, Response
from flask_user import login_required
from flask.ext.login import current_user
from typeseam.form_filler import (
    blueprint,
    queries,
    tasks
    )


@blueprint.route('/', methods=['GET'])
@login_required
def index():
    typeforms = queries.get_typeforms_for_user(current_user)
    return render_template(
        'index.html',
        typeforms=typeforms,
    )


@blueprint.route('/<typeform_key>/responses/', methods=['GET'])
@login_required
def responses(typeform_key):
    """get the responses of a particular typeform
    """
    form = queries.get_typeform(user_id=current_user.id)
    responses = queries.get_responses_for_typeform(typeform_id=form['id'])
    return render_template(
        'responses.html',
        form=form,
        responses=responses,
    )


@blueprint.route(
    '/<typeform_key>/responses/<int:response_id>/', methods=['GET'])
@login_required
def response_detail(typeform_key, response_id):
    """Show the details of a particular typeform response
    """
    response = queries.get_response_detail(current_user, response_id)
    form = queries.get_typeform(form_key=typeform_key)
    return render_template(
        "response_detail.html",
        response=response,
        form=form
        )


@blueprint.route('/<typeform_key>/responses.csv')
@login_required
def responses_csv(typeform_key):
    """Generates a csv file of all responses
    """
    csv = queries.get_responses_csv(current_user, typeform_key)
    return Response(csv, mimetype="text/csv")


##########  API Views  ################################################

@blueprint.route('/api/<typeform_key>/new_responses/', methods=['GET'])
@login_required
def remote_responses(typeform_key):
    # make an api call to Typeform
    # this can be done as a background task
    if not typeform_key:
        form_key = os.environ.get('DEFAULT_TYPEFORM_KEY')
    form = queries.get_typeform(
        form_key=typeform_key, user_id=current_user.id, model=True)
    results = tasks.get_typeform_responses(typeform_key)
    queries.save_new_typeform_data(results, form)
    responses = queries.get_responses_for_typeform(typeform_id=form.id)
    return render_template(
        "response_list.html",
        form=form,
        responses=responses)


@blueprint.route('/api/response/<response_id>/fill_pdf/', methods=['POST'])
@login_required
def fill_seamless_docs_pdf(response_id):
    # make an api call to Seamless docs
    # save the new pdf URL
    # return the new pdf
    # this can be done as a background task
    form, response = tasks.get_seamless_doc_pdf(response_id)
    return render_template(
        "pdf_button.html", form=form, response=response)
