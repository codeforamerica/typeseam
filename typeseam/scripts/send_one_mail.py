
from typeseam.app import create_app
from typeseam.auth.tasks import invite_new_user

def run():
    app = create_app()
    with app.app_context():
        status = sendgrid_email(
            subject="testing mail again",
            recipients=['benjamin.j.golder@gmail.com'],
            text_message="What is up?"
            )
        print( status )

if __name__ == '__main__':
    run()