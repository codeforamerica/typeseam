import os
import flask
from datetime import datetime
from pytz import timezone
from flask import url_for
from jinja2 import Markup


class Linkifier:
    def __init__(self, links):
        self.links = links

    def build_link(self, lookup):
        url = self.links[lookup]
        return '<a href="{}">{}</a>'.format(
            url, lookup)

    def __call__(self, content):
        output = content
        for str_lookup in self.links:
            if str_lookup in content:
                link = self.build_link(str_lookup)
                output = content.replace(str_lookup, link)
        return Markup(output)

# http://stackoverflow.com/a/5891598/399726
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

def current_local_time(fmt):
    utc_now = timezone('GMT').localize(datetime.utcnow())
    return utc_now.astimezone(timezone('US/Pacific')).strftime(fmt)


def inject_static_url():
    """Adds `STATIC_URL` variable to template context.
    """
    app = flask.current_app
    static_url = os.environ.get('STATIC_URL', app.static_url_path)
    if not static_url.endswith('/'):
        static_url += '/'
    return dict(
        static_url=static_url
    )

def add_custom_strftime():
    return dict(
        custom_strftime=custom_strftime
        )

def add_content_constants():
    from typeseam import content_constants
    linkify_links = {
        "Code for America": "https://codeforamerica.org",
        "Privacy Policy": url_for("public.privacy_policy"),
        "Clean Slate": "http://sfpublicdefender.org/services/clean-slate/",
        "clearmyrecord@codeforamerica.org": "mailto:clearmyrecord@codeforamerica.org",
        "(415) 301-6005": "tel:14153016005"
    }
    return dict(
        content=content_constants,
        linkify=Linkifier(linkify_links),
        current_local_time=current_local_time,
        current_page_url=request.url
        )
