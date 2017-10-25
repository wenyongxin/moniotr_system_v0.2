from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import Role, User
# from ..decorators import admin_required


@main.route('/')
@login_required

def index():
    return render_template('index.html')

