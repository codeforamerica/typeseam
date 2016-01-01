import sys
from typeseam.app import create_app
from typeseam.auth.tasks import invite_new_user

class MissingEmailError(Exception):
    pass

def run(emails):
    app = create_app()
    with app.app_context():
        for email in emails:
            invite_new_user(email)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise MissingEmailError("You must provide at least one email as an argument")
    else:
        run([email for email in sys.argv[1:]])