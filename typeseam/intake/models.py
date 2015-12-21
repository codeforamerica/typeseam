import datetime
from typeseam.app import db
from sqlalchemy.dialects.postgresql import JSON

class Typeform(db.Model):
    __tablename__ = 'typeform'
    id = db.Column(db.Integer, primary_key=True, index=True)
    form_key = db.Column(db.String(64))
    title = db.Column(db.String(128))

class TypeformResponse(db.Model):
    __tablename__ = 'response'
    id = db.Column(db.Integer, primary_key=True, index=True)
    date_received = db.Column(db.DateTime)
    answers = db.Column(JSON)
    answers_translated = db.Column(db.Boolean(), default=False)
    seamless_submitted = db.Column(db.Boolean(), default=False)
    seamless_key = db.Column(db.String(128))
    pdf_url = db.Column(db.String(128))

    def __repr__(self):
        return "<TypeformResponse received='{}'>".format(str(self.date_received))