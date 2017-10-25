# coding: utf-8

from flask import Blueprint


report = Blueprint('report', __name__)

import views,month_repo,anomaly_record,trouble_repo  # 引用视图和模型
# from app import views