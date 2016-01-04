import datetime
from typeseam.extensions import db
from sqlalchemy.dialects.postgresql import JSON


class Typeform(db.Model):
    __tablename__ = 'form_filler_typeform'
    id = db.Column(db.Integer, primary_key=True, index=True)
    form_key = db.Column(db.String(64))
    title = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    added_on = db.Column(db.DateTime(), server_default=db.func.now())
    response_count = db.Column(db.Integer, default=0)
    latest_response = db.Column(db.DateTime())

    def __repr__(self):
        return '<Typeform:"{}", title="{}">'.format(self.form_key, self.title)


class SeamlessDoc(db.Model):
    __tablename__ = 'form_filler_seamlessdoc'
    id = db.Column(db.Integer, primary_key=True, index=True)
    seamless_key = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    typeform_id = db.Column(
        db.Integer, db.ForeignKey('form_filler_typeform.id'))

    def __repr__(self):
        return '<SeamlessDoc:"{}">'.format(self.seamless_key)


class TypeformResponse(db.Model):
    __tablename__ = 'form_filler_response'
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    typeform_id = db.Column(
        db.Integer, db.ForeignKey('form_filler_typeform.id'))
    seamless_id = db.Column(
        db.Integer, db.ForeignKey('form_filler_seamlessdoc.id'))
    date_received = db.Column(db.DateTime)
    answers = db.Column(JSON)
    answers_translated = db.Column(db.Boolean(), default=False)
    seamless_submitted = db.Column(db.Boolean(), default=False)
    seamless_submission_id = db.Column(db.String(128))
    pdf_url = db.Column(db.String(128))

    def __repr__(self):
        return "<TypeformResponse received='{}'>".format(
            str(self.date_received))
