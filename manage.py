#!/usr/bin/env python
#ecoding:utf-8
from app import create_app, db, make_celery, filter
from app.models import User, Role, Permission
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)
celery = make_celery(app)
filter.custom_filters(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server( host = '0.0.0.0', port = 9090, use_debugger = True, threaded=True))







if __name__ == '__main__':
#	app.run()
    manager.run()
