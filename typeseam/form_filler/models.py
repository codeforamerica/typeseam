import datetime, uuid, os
from pytz import timezone
from ago import human
from typeseam.extensions import db
from typeseam.settings import PROJECT_ROOT
from typeseam.context_processors import namify

from sqlalchemy.dialects.postgresql import JSON

from typeseam.form_filler.pdfparser import PDFParser

pdfparser = PDFParser()
gmt = timezone('GMT')
pacific = timezone('US/Pacific')

def PDT(dt):
    return gmt.localize(dt).astimezone(pacific)

def gen_uuid():
    return uuid.uuid4().hex

def yesno(s, key=None):
    if not key:
        return 'Off'
    result = s.answers.get(key, '')
    if not result:
        return 'Off'
    if result in ('yes', 'no'):
        return result.capitalize()


nice_contact_choices = {
    'voicemail': 'Voicemail',
    'sms': 'Text Message',
    'email': 'Email',
    'snailmail': 'Paper mail'
}

def get_formatted_dob(s):
    return '{}/{}/{}'.format(
                s.answers.get('dob_month', ''),
                s.answers.get('dob_day', ''),
                s.answers.get('dob_year', ''))

def fmt_ssn(s, prefix='SS# '):
    ssn = s.answers.get('ssn', '')
    if ssn:
        digits = ''.join([d for d in ssn if d.isnumeric()])
        return '{}{}-{}-{}'.format(prefix, digits[:3], digits[3:5], digits[5:])
    return ''

clean_slate_translator = {
            'Address City': 'address_city',
            'Address State': 'address_state',
            'Address Street': 'address_street',
            'Address Zip': 'address_zip',
            'Arrested outside SF': lambda s: yesno(s, 'rap_outside_sf'),
            'Cell phone number': 'phone_number',
            'Charged with a crime': lambda s: yesno(s, 'being_charged'),
            'Date': lambda s: PDT(s.date_received).strftime('%-m/%-d/%Y'),
            'Date of Birth': get_formatted_dob,
            'Dates arrested outside SF': 'when_where_outside_sf',
            'Drivers License': 'drivers_license_number',
            'Email Address': 'email',
            'Employed': lambda s: yesno(s, 'currently_employed'),
            'First Name': lambda s: namify(s.answers.get('first_name','')),
            'Home phone number': '',
            'How did you hear about the Clean Slate Program': 'how_did_you_hear',
            'If probation where and when?': lambda s: '{} {}'.format(
                s.answers.get('where_probation_or_parole'),
                s.answers.get('when_probation_or_parole')),
            'Last Name': lambda s: namify(s.answers.get('last_name','')),
            'MI': lambda s: s.answers.get('middle_name', '')[:1],
            'May we leave voicemail': lambda s: yesno(s),
            'May we send mail here': lambda s: yesno(s),
            'Monthly expenses': 'monthly_expenses',
            'On probation or parole': lambda s: yesno(s, 'on_probation_parole'),
            'Other phone number': '',
            'Serving a sentence': lambda s: yesno(s, 'serving_sentence'),
            'Social Security Number': lambda s: fmt_ssn(s, ''),
            'US Citizen': lambda s: yesno(s, 'us_citizen'),
            'What is your monthly income': 'monthly_income',
            'Work phone number': '',
            'DOB': get_formatted_dob,
            'SSN': fmt_ssn,
            'FirstName': lambda s: namify(s.answers.get('first_name','')),
            'LastName': lambda s: namify(s.answers.get('last_name',''))
        }


PDFS = {
    'clean_slate': {
        'translator': clean_slate_translator,
        'pdf_path': 'CleanSlateCombined.pdf'}}

class FormSubmission(db.Model):
    __tablename__ = 'form_filler_submission'
    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String(), default=gen_uuid)
    date_received = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(), default='new')
    county = db.Column(db.String(), default='sanfrancisco')
    answers = db.Column(JSON)

    @classmethod
    def fill_many_pdfs(cls, pdf_key, submissions):
        pdf_path = os.path.join(PROJECT_ROOT, 'data/pdfs', PDFS[pdf_key]['pdf_path'])
        translator = PDFS[pdf_key]['translator']
        answers = [s.translate(translator) for s in submissions]
        if len(answers) > 1:
            return pdfparser.fill_many_pdfs(pdf_path, answers)
        else:
            return pdfparser.fill_pdf(pdf_path, answers[0])

    def get_local_date_received(self, timezone_name='US/Pacific'):
        local_tz = timezone(timezone_name)
        return gmt.localize(self.date_received).astimezone(local_tz)

    def fill_pdf(self, pdf_key):
        if pdf_key not in PDFS:
                raise KeyError("no pdf with that key")
        pdf_path = os.path.join(PROJECT_ROOT, 'data/pdfs', PDFS[pdf_key]['pdf_path'])
        translator = PDFS[pdf_key]['translator']
        data = self.translate(translator)
        return pdfparser.fill_pdf(pdf_path, data)

    def translate(self, translator):
        result = {}
        for key, extractor in translator.items():
            if hasattr(extractor, '__call__'):
                result[key] = extractor(self)
            else:
                result[key] = self.answers.get(extractor, '')
        return result

    def get_contact_preferences(self):
        preferences = []
        for k in self.answers:
            if "prefers" in k:
                preferences.append(k[8:])
        return [nice_contact_choices[m] for m in preferences]

    def was_opened(self, logs):
        # this assumes logs are sorted from most recent to oldest
        for log in logs:
            if log.user == 'Louise.Winterstein@sfgov.org':
                return log.datetime
        return False

    def was_added(self, logs):
        for log in logs:
            if log.event_type == 'added' and log.user == 'Louise.Winterstein@sfgov.org':
                return log.datetime
        return False



class LogEntry(db.Model):
    __tablename__ = "form_filler_logentry"
    id = db.Column(db.Integer, primary_key=True, index=True)
    datetime = db.Column(db.DateTime, index=True)
    user = db.Column(db.String())
    submission_key = db.Column(db.String(), index=True)
    event_type = db.Column(db.String())
    source = db.Column(db.String(), default='front')

    @classmethod
    def from_parsed_front_event(cls, event):
        return cls(
            datetime=datetime.datetime.fromtimestamp(
                event['time']),
            user=event.get('by', ''),
            submission_key=event['key'],
            event_type=event['type']
            )

    def pacific(self, fmt=None):
        dtz = gmt.localize(
                    self.datetime
                    ).astimezone(pacific)
        if fmt:
            return dtz.strftime(fmt)
        return dtz

    def day(self):
        return self.pacific('%Y-%m-%d')


class Typeform(db.Model):
    __tablename__ = 'form_filler_typeform'
    id = db.Column(db.Integer, primary_key=True, index=True)
    live_url = db.Column(db.String(128))
    edit_url = db.Column(db.String(128))
    form_key = db.Column(db.String(64))
    title = db.Column(db.String(128))
    translator = db.Column(JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    added_on = db.Column(db.DateTime(), server_default=db.func.now())
    latest_response = db.Column(db.DateTime())
    # a dynamic 'responses' relationship that'll perform the query when accessed
    responses = db.relationship('TypeformResponse', backref='typeform', order_by='desc(TypeformResponse.date_received)')

    def __repr__(self):
        return '<Typeform:"{}", title="{}">'.format(self.form_key, self.title)


class SeamlessDoc(db.Model):
    __tablename__ = 'form_filler_seamlessdoc'
    id = db.Column(db.Integer, primary_key=True, index=True)
    seamless_key = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('auth_user.id'))
    added_on = db.Column(db.DateTime(), server_default=db.func.now())

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







