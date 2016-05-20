import sys
from typeseam.app import create_app
from typeseam.form_filler import tasks


def run():
    app = create_app()
    with app.app_context():
        tasks.send_unopened_apps_notification()

if __name__ == '__main__':
    run()