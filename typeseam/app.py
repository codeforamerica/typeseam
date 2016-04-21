import os
from flask import Flask

from typeseam.extensions import (
    db, migrate, seamless_auth, ma, csrf, mail, sg
    )

from typeseam.setup_logging import register_logging
from flask_user import (
    UserManager, SQLAlchemyAdapter
    )
from typeseam import constants


def create_app():
    config = os.environ.get('CONFIG', 'typeseam.settings.DevConfig')
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    register_context_processors(app)
    register_logging(app, config)
    @app.before_first_request
    def setup():
        load_initial_data(app)
    return app


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    seamless_auth.init_app(app)
    ma.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    sg.init_app(app)

    from flask_sslify import SSLify
    # only trigger SSLify if the app is running on Heroku
    if 'DYNO' in os.environ:
        SSLify(app)

    # setup flask-user
    from typeseam.auth.models import User, UserInvitation
    db_adapter = SQLAlchemyAdapter(
        db, User, UserInvitationClass=UserInvitation)
    user_manager = UserManager(db_adapter, app)
    # use sendgrid for sending emails
    from typeseam.auth.tasks import sendgrid_email
    user_manager.send_email_function = sendgrid_email


def register_blueprints(app):
    from typeseam.form_filler import blueprint as form_filler
    app.register_blueprint(form_filler)
    from typeseam.auth import blueprint as auth
    app.register_blueprint(auth)
    from typeseam.public import blueprint as public
    app.register_blueprint(public)


def register_context_processors(app):
    from typeseam.context_processors import (
        add_custom_strftime,
        inject_static_url,
        add_content_constants,
        )
    app.context_processor(inject_static_url)
    app.context_processor(add_custom_strftime)
    app.context_processor(add_content_constants)


def load_initial_data(app):
    with app.app_context():
        if os.environ.get('MAKE_DEFAULT_USER', False):
            # create default user
            email = os.environ.get(
                'DEFAULT_ADMIN_EMAIL', 'someone@example.com')
            password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'Passw0rd')
            from typeseam.auth.queries import create_user
            user = create_user(email, password)
            # create default typeform
            form_key = os.environ.get('DEFAULT_TYPEFORM_KEY', '')
            title = os.environ.get('DEFAULT_TYPEFORM_TITLE', '')
            live_url = os.environ.get('DEFAULT_TYPEFORM_LIVE_URL', '')
            edit_url = os.environ.get('DEFAULT_TYPEFORM_EDIT_URL', '')
            translator_key = os.environ.get('DEFAULT_TYPEFORM_TRANSLATOR', 'TRANSLATOR_A')
            translator = getattr(constants, translator_key)
            if form_key and title:
                from typeseam.form_filler.queries import create_typeform
                create_typeform(form_key=form_key, title=title, user_id=user.id,
                                live_url=live_url, edit_url=edit_url, translator=translator)
        if app.config.get('LOAD_FAKE_DATA', False) and not app.testing:
            from typeseam.form_filler.queries import get_response_count
            from tests.mock.factories import generate_fake_data
            if get_response_count() < 10:
                results = generate_fake_data(num_users=10)
                print(results[0])
