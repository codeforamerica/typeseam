
from typeseam.utils import SeamlessDocsAPIAuth
seamless_auth = SeamlessDocsAPIAuth()

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_marshmallow import Marshmallow
ma = Marshmallow()

from flask_migrate import Migrate
migrate = Migrate()

from flask_login import LoginManager
login_manager = LoginManager()

from flask_wtf.csrf import CsrfProtect
csrf = CsrfProtect()