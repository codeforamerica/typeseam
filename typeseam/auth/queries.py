from datetime import datetime
from flask import current_app as app
from typeseam.app import db

from typeseam.auth.models import User

def create_user(email, password, active=True, confirmed_at=None):
    if confirmed_at == None:
        confirmed_at = datetime.utcnow()
    user = User(email=email,
                password=hash_password(password),
                active=active,
                confirmed_at=confirmed_at)
    db.session.add(user)
    db.session.commit()
    return user

def get_user_by_email(email):
    user, _ = app.user_manager.find_user_by_email(email)
    return user

def hash_password(raw_password):
    return app.user_manager.hash_password(raw_password)