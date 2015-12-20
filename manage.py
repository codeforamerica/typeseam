import os
from flask_migrate import MigrateCommand
from flask_script import Manager, Shell, Server
from typeseam.app import create_app, db

app = create_app()
manager = Manager(app)

def _make_context():
    """Return context dict for a shell session so you can access
    app and db by default.
    """
    return {'app': app, 'db': db}

manager.add_command('server', Server(port=os.environ.get('PORT', 9000)))
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()