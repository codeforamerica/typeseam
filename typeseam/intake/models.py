import datetime
from typeseam.app import db
from sqlalchemy.dialects.postgresql import JSON


class TypeformResponse(db.Model):
    __tablename__ = 'response'
    id = db.Column(db.Integer, primary_key=True, index=True)
    date_received = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    data = db.Column(JSON)

