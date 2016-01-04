import os
import time
import hmac
import hashlib
from requests.auth import AuthBase


def build_seamless_auth():
    return SeamlessDocsAPIAuth()


class SeamlessDocsAPIAuth(AuthBase):
    """Sets up the HMAC Signature-based authorization on
        Seamless Docs API requests
        http://developers.seamlessdocs.com/v1.2/docs/getting-started
        http://developers.seamlessdocs.com/v1.2/docs/signing-requests
    """
    def __init__(self, app=None):
        self.config = {}
        self.set_config(app)

    def init_app(self, app):
        self.set_config(app)

    def config_from_env(self):
        nonce = os.environ.get('NONCE', None)
        if not nonce:
            nonce = os.environ.get('SECRET_KEY', 'ministryOfSillyWalks')
        self.config.update(
            nonce=nonce,
            api_key=os.environ.get('SEAMLESS_DOCS_API_KEY', ''),
            api_secret=os.environ.get('SEAMLESS_DOCS_API_SECRET', '')
            )

    def config_from_app(self, app):
        nonce = app.config.get('NONCE', None)
        if not nonce:
            nonce = app.config.get('SECRET_KEY', 'ministryOfSillyWalks')
        self.config.update(
            nonce=nonce,
            api_key=app.config.get('SEAMLESS_DOCS_API_KEY', ''),
            api_secret=app.config.get('SEAMLESS_DOCS_API_SECRET', '')
            )

    def set_config(self, app=None):
        if app:
            self.config_from_app(app)
        else:
            self.config_from_env()

    def calculate(self, base, secret):
        return hmac.new(
            key=secret.encode('utf-8'),
            msg=base.encode('utf-8'),
            digestmod=hashlib.sha256
            ).hexdigest()

    def build_header(self, signature):
        auth_header_params = {
            'api_key': self.config['api_key'],
            'nonce': self.config['nonce'],
            'signature': signature
        }
        auth_template = "HMAC-SHA256 api_key={api_key} nonce={nonce} signature={signature}"
        return auth_template.format(**auth_header_params)

    def __call__(self, request, nonce=None):
        # create signature base
        method = request.method
        uri = request.url.split('api')[-1]
        # python's time.time is floating point & too precise
        timestamp = str(int(time.time()))
        if nonce is None:
            nonce = self.config['nonce']
        base = '+'.join([method, uri, timestamp, nonce])
        # '<request_method>+<uri>+<timestamp>[+<nonce>]'
        signature = self.calculate(base, self.config['api_secret'])
        request.headers.update({
            'Authorization': self.build_header(signature),
            'Date': timestamp
            })
        return request
