import os
import flask


# http://stackoverflow.com/a/5891598/399726
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

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