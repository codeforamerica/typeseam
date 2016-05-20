
import os, io
from datetime import datetime, timedelta
from flask import (
    request, redirect, render_template, jsonify,
    Response, url_for, send_file, abort
    )
from flask_user import login_required
from flask.ext.login import current_user
from typeseam.form_filler import (
    blueprint,
    queries,
    tasks
    )
from typeseam import content_constants as content
from typeseam.settings import PROJECT_ROOT


def get_response_date():
    now = datetime.now()
    four_weeks = timedelta(days=28)
    return now + four_weeks


@blueprint.route('/', methods=['GET'])
def index():
    return render_template('main_splash.html',
        page_title=content.topbar,
        body_class="splash",
        response_estimate=get_response_date())


@blueprint.route('/sanfrancisco/', methods=['GET', 'POST'])
def county_application():
    if request.method == 'GET':
        return render_template('county_application_form.html')
    else:
        # TODO: add validation and error handling
        form_data = request.form.to_dict()
        submission = queries.save_new_form_submission(form_data)
        tasks.send_submission_notification(submission)
        return redirect(url_for('form_filler.thanks'))


@blueprint.route('/sanfrancisco/applications/', methods=['GET'])
@login_required
def applications_index():
    tasks.sync_logentries_with_front()
    submissions = queries.get_submissions_with_logs()
    return render_template("app_index.html", submissions=submissions,
        body_class="admin")


@blueprint.route('/sanfrancisco/<submission_uuid>/')
@login_required
def get_filled_pdf(submission_uuid):
    submission = queries.get_submission_by_uuid(submission_uuid)
    pdf = submission.fill_pdf('clean_slate')
    tasks.send_submission_viewed_notification(submission)
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf')

@blueprint.route('/sanfrancisco/bundle/')
@login_required
def get_application_bundle():
    uuids = request.args.get('keys', '').split('|')
    submissions = queries.get_submissions(uuids)
    if submissions:
        return render_template('app_bundle.html',
            submissions=submissions,
            count=len(submissions),
            body_class="admin")
    else:
        return redirect(url_for('form_filler.applications_index'))


@blueprint.route('/sanfrancisco/pdfs/')
@login_required
def get_multiple_filled_pdfs():
    uuids = request.args.get('keys', '').split('|')
    if uuids:
        pdf = tasks.build_multi_submission_pdf(uuids)
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf')


@blueprint.route('/sanfrancisco/unopened/')
@login_required
def unopened_apps():
    submissions = queries.get_unopened_submissions()
    uuids = '|'.join([s.uuid for s in submissions])
    return redirect(
        url_for('form_filler.get_application_bundle',
            keys=uuids))

@blueprint.route('/sanfrancisco/unopened/pdf/')
@login_required
def unopened_apps_pdf():
    pdf = tasks.build_unopened_submissions_pdf()
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf')


@blueprint.route('/sanfrancisco/add_many/')
@login_required
def multi_mark_as_added():
    uuids = request.args.get('keys', '').split('|')
    if uuids:
        queries.save_multiple_logentries(uuids, 'added')
    return redirect(url_for(
        'form_filler.get_application_bundle',
        keys='|'.join(uuids)
        ))


@blueprint.route('/sanfrancisco/<submission_uuid>/add/')
@login_required
def mark_as_added(submission_uuid):
    queries.save_new_logentry(submission_uuid, 'added')
    return redirect(url_for('form_filler.applications_index'))


@blueprint.route('/sanfrancisco/<submission_uuid>/delete/')
@login_required
def delete_page(submission_uuid):
    submission = queries.get_submission_by_uuid(submission_uuid)
    return render_template('delete_page.html',
        page_title="Delete Application",
        submission=submission,
        body_class="admin")

@blueprint.route('/sanfrancisco/<submission_uuid>/delete-forever/')
@login_required
def definitely_delete(submission_uuid):
    queries.delete_submission_forever(submission_uuid)
    return redirect(url_for('form_filler.applications_index'))


@blueprint.route('/thanks/', methods=['GET'])
def thanks():
    return render_template('thanks.html')

@blueprint.route('/stats/', methods=['GET'])
def analytics():
    tasks.sync_logentries_with_front()
    stats = queries.get_stats()
    return render_template('analytics.html', stats=stats,
        body_class="admin")

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
