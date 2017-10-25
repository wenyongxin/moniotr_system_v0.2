from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views, login, func, permission, urls
