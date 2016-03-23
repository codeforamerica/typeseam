
from flask import render_template
from typeseam.public import blueprint


@blueprint.route('/privacy/')
def privacy_policy():
    return render_template('privacy_policy.html')