import os
from flask import Flask
from pprint import pprint

from typeseam.extensions import (
    db, migrate, seamless_auth
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

def register_blueprints(app):
    from typeseam.intake import blueprint as intake
    app.register_blueprint(intake)