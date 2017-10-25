from flask import Blueprint

monitor = Blueprint('monitor', __name__)

from . import views, interface, views_monitor, game_ascription, scan_page