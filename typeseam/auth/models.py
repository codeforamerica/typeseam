import datetime
from typeseam.extensions import db
from flask_user import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'auth_user'
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __repr__(self):
        return '<auth.User(email="{}")>'.format(self.email)
