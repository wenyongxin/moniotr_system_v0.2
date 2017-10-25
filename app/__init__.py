#!/usr/bin/env python
#ecoding:utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from celery import Celery
from celery import platforms  #如果你不是linux的root用户，这两行没必要
import config


csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def make_celery(app):
    celery = Celery('manage', broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    #创建report app实例
    from .report import report as report_blueprint
    app.register_blueprint(report_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .business import business
    app.register_blueprint(business)

    from .monitor import monitor
    app.register_blueprint(monitor)

    return app
