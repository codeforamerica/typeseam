import sys
import os
import typeseam
from typeseam import constants
from typeseam.app import create_app
from typeseam.auth.queries import create_user
from typeseam.form_filler.queries import create_typeform
path = os.path.dirname(os.path.dirname(typeseam.__file__))
sys.path.insert(0, path)
from tests.mock.factories import generate_fake_responses

def run(email=None, password=None):

    app = create_app()
    with app.app_context():
        user = create_user(email, password)
        form_key = os.environ.get('DEFAULT_TYPEFORM_KEY', '')
        title = os.environ.get('DEFAULT_TYPEFORM_TITLE', '')
        live_url = os.environ.get('DEFAULT_TYPEFORM_LIVE_URL', '')
        edit_url = os.environ.get('DEFAULT_TYPEFORM_EDIT_URL', '')
        translator_key = os.environ.get('DEFAULT_TYPEFORM_TRANSLATOR', 'TRANSLATOR_A')
        translator = getattr(constants, translator_key)
        form = create_typeform(form_key, title=title, user_id=user.id, live_url=live_url,
            edit_url=edit_url, translator=translator)
        generate_fake_responses(form, 20)

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
