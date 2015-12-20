import requests
from pprint import pprint
from typeseam.app import create_app, db

FORM_KEY = 'o8MrpO'
BASE_URL = 'https://api.typeform.com/v0/form/' + FORM_KEY
def run():
    app = create_app()
    with app.app_context():
        args = {
            'key': app.config.get('TYPEFORM_API_KEY', None),
            'completed': 'true'}
        pprint(args)
        r = requests.get(BASE_URL, params=args)
        print(r.url)
        pprint(r.json())


if __name__ == '__main__':
    run()