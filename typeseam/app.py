import os
from flask import Flask


from typeseam.extensions import (
    db, migrate, seamless_auth, ma
    )
from flask_user import (
    UserManager, SQLAlchemyAdapter
    )

def create_app():
    config = os.environ['CONFIG']
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    return app

def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    seamless_auth.init_app(app)
    ma.init_app(app)

    # setup flask-user
    from typeseam.auth.models import User
    db_adapter = SQLAlchemyAdapter(db, User)
    user_manager = UserManager(db_adapter, app)

def register_blueprints(app):
    from typeseam.intake import blueprint as intake
    app.register_blueprint(intake)
    from typeseam.auth import blueprint as auth
    app.register_blueprint(auth)
