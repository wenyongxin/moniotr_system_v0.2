#coding: utf-8

import time,datetime,json,re,calendar,sys
from sqlalchemy import or_
from app.main import main
from app import db, csrf
from flask_login import login_required
from app.decorators import permission_required
from flask import render_template, flash, redirect, session, url_for, request,Response
from app.models import Sections, Permission_Model, Permission,Maintenance,Zabbix_group
from app.scripts.zabbix import zabbix_login,get_api_data
from app.scripts.tools import delete_dbs

sys.path.append('../..')
import config



@main.route('/sysmg', methods=['POST','GET'])
@permission_required(Permission.user, path='/sysmg', app='main')
@login_required
@csrf.exempt
#故障报告展示
def sysmg():
    return render_template('system_manage.html',**locals())

