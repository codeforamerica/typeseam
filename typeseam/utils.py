from requests.auth import AuthBase
import time
import hmac
import hashlib


class SeamlessDocsAPIAuth(AuthBase):
    """Sets up the HMAC Signature-based authorization on
        Seamless Docs API requests
        http://developers.seamlessdocs.com/v1.2/docs/getting-started
        http://developers.seamlessdocs.com/v1.2/docs/signing-requests
    """
    def __init__(self, app=None):
        self.config = {}
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.config.update({
            'nonce': app.config.get('SECRET_KEY', 'ministryOfSillyWalks'),
            'api_key': app.config.get('SEAMLESS_DOCS_API_KEY'),
            'api_secret': app.config.get('SEAMLESS_DOCS_API_SECRET')
            })

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
        if nonce == None:
            nonce = self.config['nonce']
        base = '+'.join([method, uri, timestamp, nonce])
        # '<request_method>+<uri>+<timestamp>[+<nonce>]'
        signature = self.calculate(base, self.config['api_secret'])
        request.headers.update({
            'Authorization': self.build_header(signature),
            'Date': timestamp
            })
        return request