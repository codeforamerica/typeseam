
from flask import render_template, jsonify, Response
from typeseam.intake import (
    blueprint,
    queries,
    tasks
    )
FORM = {
        'id': 1,
        'title': 'Clean Slate SF',
        'form_key': 'o8MrpO',
        'edit_url': 'https://admin.typeform.com/form/1084993/fields/',
        'live_url': 'https://bgolder.typeform.com/to/o8MrpO',
    }
@blueprint.route('/', methods=['GET'])
def local_responses():
    # get serialized existing responses
    responses = queries.most_recent_responses()
    # render them in a template
    return render_template(
        'index.html',
        form=FORM,
        responses=responses,
    )

@blueprint.route('/response/<int:response_id>')
def response_detail(response_id):
    response = queries.get_response_detail(response_id)
    return render_template(
        "response_detail.html",
        response=response,
        form=FORM
        )

@blueprint.route('/responses.csv')
def responses_csv():
    csv = queries.get_responses_csv()
    return Response(csv, mimetype="text/csv")

@blueprint.route('/api/new_responses', methods=['GET'])
def remote_responses():
    # make an api call to Typeform
    # this can be done as a background task
    responses = tasks.get_typeform_responses()
    return render_template(
        "response_list.html",
        responses=responses)

@blueprint.route('/api/get_pdf/<response_id>', methods=['GET'])
def get_seamless_docs_pdf(response_id):
    # make an api call to Seamless docs
    # save the new pdf URL
    # return the new pdf
    # this can be done as a background task
    response = tasks.get_seamless_doc_pdf(response_id)
    return render_template("response_listing.html", response=response)
