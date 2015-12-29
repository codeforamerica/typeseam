from datetime import datetime
from flask import current_app as app
from typeseam.app import db

from typeseam.auth.models import User

def create_user(email, password):
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email,
                    password=app.user_manager.hash_password(password),
                    active=True,
                    confirmed_at=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
    return user

def get_user_by_email(email):
    user, _ = app.user_manager.find_user_by_email(email)
    return user