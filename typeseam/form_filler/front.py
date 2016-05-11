from datetime import datetime, timezone
from pytz import timezone as ptimezone
import re
import json
import requests


class Front:

    def __init__(self, token):
        self.headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Accept': 'application/json'
        }
        self.event_types = 'q[types][]=inbound&q[types][]=outbound'
        self.root_url = 'https://api2.frontapp.com/events?'
        self.payload = []

    def get_events(self, after=None):
        self.payload = []
        request_url = self.root_url + self.event_types
        if after:
            request_url += '&q[after]={}'.format(after)
        self.pull_payload(request_url)
        return self.parse_events()

    def pull_payload(self, url):
        next_page = url
        while next_page:
            response = requests.get(
                next_page, headers=self.headers)
            data = response.json()
            self.payload.extend(data['_results'])
            next_page = data["_pagination"]["next"]

    def parse_events(self):
        events = []
        for event in self.payload:
            data = event["conversation"]
            message = data["last_message"]
            if message["type"] == "email":
                message["subject"] = data["subject"]
                if is_referral(message):
                    events.append(get_referral_info(message))
                elif is_submission(message):
                    events.append(get_submission_info(message))
                elif is_opening(message):
                    events.append(get_opening_info(message))
        return events


def get_opening_info(msg):
    return {
        "type": "opened",
        "time": get_datetime(msg),
        "by": get_opener(msg),
        "key": is_opening(msg)
    }


def is_from_cmr(msg):
    for entity in msg["recipients"]:
        if entity["handle"] == "clearmyrecord@codeforamerica.org":
            return entity["role"] == "from"
    return False

def is_to_louise(msg):
    for entity in msg["recipients"]:
        if entity["handle"] == "louise.winterstein@sfgov.org":
            return entity["role"] == "to"
    return False


def is_from_server(msg):
    for entity in msg["recipients"]:
        if entity["handle"] == "no-reply@codeforamerica.org":
            return entity["role"] == "from"
    return False


def get_referral_author(msg):
    return msg["author"]["username"]


def get_datetime(msg):
    return msg["created_at"]

def get_referral_key(msg):
    pattern = re.compile(
            "\.org/sanfrancisco/(?P<key>[0-9a-f]+)/"
            )
    results = pattern.findall(msg["text"])
    if results and len(results) == 1:
        return results[0]
    else:
        raise Exception(
            "Couldn't find a uuid in {}".format(
                json.dumps(msg, indent=2)
                ))

def utc_to_cali(timestamp, fmt="%c"):
    PDT = ptimezone('US/Pacific')
    dt = datetime.fromtimestamp(timestamp, timezone.utc)
    return dt.astimezone(PDT).strftime(fmt)


def is_referral(msg):
    return is_from_cmr(msg) and is_to_louise(msg)


def get_referral_info(msg):
    return {
        "type": "referred",
        "by": get_referral_author(msg),
        "time": get_datetime(msg),
        "key": get_referral_key(msg)
    }


def is_submission(msg):
    srch = "New application to http://clearmyrecord.codeforamerica.org/"
    return srch in msg["subject"]


def get_submission_info(msg):
    return {
        "type": "received",
        "time": get_datetime(msg),
        "key": get_referral_key(msg)
    }

def get_opener(msg):
    srch = "viewed by "
    idx = msg["subject"].rfind(srch)
    email = msg["subject"][idx + len(srch):]
    return email


def is_opening(msg):
    pattern = re.compile("Application (?P<key>[0-9a-f]+) viewed by")
    results = pattern.findall(msg["subject"])
    if results:
        return results[0]
    return False
