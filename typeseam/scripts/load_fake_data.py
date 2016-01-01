import sys
from typeseam.app import create_app
from tests.mock.factories import generate_fake_data

def run():
    app = create_app()
    with app.app_context():
        generate_fake_data()

if __name__ == '__main__':
    run()