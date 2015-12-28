from flask import render_template, jsonify, Response
from typeseam.auth import (
    blueprint,
    )

@blueprint.route('/login', methods=['GET'])
def login(next='/'):
    return render_template(
        'auth/login.html', page_title='Log in', next=next
    )
