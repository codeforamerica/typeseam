import requests
from pprint import pprint
from typeseam.app import create_app, db, seamless_auth


BASE_URL = 'https://cleanslate.seamlessdocs.com/api/'
FORM_ID = 'CO15121000011304402'
API_URL = 'form/{}/elements'.format(FORM_ID)

def run():
    app = create_app()
    with app.app_context():
        r = requests.get(BASE_URL + API_URL, auth=seamless_auth)
        pprint(r.json())

if __name__ == '__main__':
    run()