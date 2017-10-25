#!/usr/bin/env python
#ecoding:utf-8

import json
import sys

from flask import render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required
from . import business
from ..scripts.tools import save_db, delete_db
from ..scripts.zabbix_manage import manage_zabbix, zabbix_tools
from ..decorators import admin_required,permission_required
from .. import csrf
from models import Manager_business
from ..models import Sections,Permission

sys.path.append('../..')
import config
from models import History_Number, db
from ..scripts.time_manage import date_time, date_to_strftime, strftime_to_date, db_datetime_string
from ..scripts.redis_manage import Efun_Redis
from ..scripts.zabbix_manage import manage_zabbix

#全局变量
zabbix = manage_zabbix()




#通过主机的ip地址获取对应的主机下面的item项目
@business.route('/search', methods=['GET','POST'])
@csrf.exempt
@admin_required
@login_required
def search_info():
    if request.is_xhr and request.method == 'GET':
        id = request.args.get('id')
        html_data = {
            'sections':zabbix_tools.return_sections(),
            'button_name':u'创建',
            'button_type':'create',
            'sort':zabbix_tools.return_sort()
        }
        if int(id) != 0:
            db_datas = Manager_business.query.get(id)
            check_items = [ int(item) for item in db_datas.items.split(',') ]
            check_items.sort()
            html_data['button_name'] = u'修改'
            html_data['button_type'] = 'edit'
            html_data['ipaddress'] = db_datas.hostip
            html_data['db_items'] = db_datas
            html_data['new_datas'] = zabbix.return_views_info(db_datas.hostip, check_items, select=True)


        return render_template('manager/manager_business_alert.html', **html_data)

#通过ajax方式传入ip地址。查看该ip下面的所有信息
@business.route('/search_ip', methods=['GET'])
@csrf.exempt
@admin_required
@login_required
def search_ip():
    if request.is_xhr and request.method == 'GET':
        ip = request.args.get('ip')
        new_datas = zabbix.return_views_info(ip)
        html = render_template('temp/zabbix_applications_items.html', new_datas=new_datas)
        return html


#通用的动作函数，可以做增、删、改的基本操作
@business.route('/action/<action>/<id>', methods=['POST'])
@csrf.exempt
@admin_required
@login_required
def action_business(action,id):

    if request.is_xhr and request.method == 'POST':

        #如果action为delete不做数据获取
        if action.encode('utf-8') != 'delete':
            web_name = request.form.get('name')
            web_hostip = request.form.get('hostip')
            web_describe = request.form.get('describe')
            web_sections_id = request.form.get('sections_id')
            web_items = request.form.get('items')
            web_sort = zabbix_tools.return_sort()[int(request.form.get('sort'))]

        if action.encode('utf-8') == 'create' and int(id) == 0:
            business = Manager_business(name=web_name,
                                        describe=web_describe,
                                        sort=web_sort,
                                        items=web_items,
                                        hostip=web_hostip)
            business.sections = Sections.query.get(web_sections_id)
            save_db(business)
            flash({'type':'ok','message':u'创建成功'})
        elif action.encode('utf-8') == 'edit' and int(id) != 0:
            business = Manager_business.query.get(id)
            business.name = web_name
            business.describe = web_describe
            business.sort = web_sort
            business.items = web_items
            business.hostip = web_hostip
            business.sections = Sections.query.get(web_sections_id)
            save_db(business)
            flash({'type':'ok','message':u'更新成功'})
        elif action.encode('utf-8') == 'delete' and int(id) != 0:
            business = Manager_business.query.get(id)
            delete_db(business)
            flash({'type':'ok','message':u'删除成功'})
        else:
            flash({'type':'error','message':u'创建失败'})
        return jsonify({'code':200})




#业务url页面。在该url上实现业务展示
@business.route('/business/<url>')
@login_required
@permission_required(Permission.user)
def show_graphs(url):
    get_url = request.path
    if url in get_url:
        try:
            now_items = []
            section = Sections.query.filter_by(href = get_url).first()
            for bus in section.business:
                now_items += bus.items.split(',')

            #将所有item的值保存到memcached中
            zabbix.items_names(url, now_items)

            html_data = {
                'name':section.name,
                'data': section.business,
                'url':url
            }
            return render_template('business/business_templates.html', **html_data)
        except BaseException,e:
            print e
            flash({'type':'error','message':u'访问 %s 错误' %request.path})
            return redirect(url_for("main.index"))


#ajax方式获取页面数据
#1、确认开始数据是不是当天
#2、开始时间到结束时间是不是24小时范围内
#3、如果是则从redis中读取
#4、如果不是则从mysql中读取
#5、按照返回30个元素进行计算调试。日期则提取最大值对应的时间点
@business.route('/<url>/ajax.json', methods=['GET'])
@login_required
def ajax_get(url):
    return_jsons,end = {}, -1

    #数据处理的内部函数
    def return_items_datas(section, type='redis'):
        infos = []
        for bus in section.business:
            datas = []
            for item in bus.items.split(','):
                name = json.loads(Efun_Redis.redis_get(url))[item]
                if type == 'redis':
                    datas += [{'name':name, 'data':[ float(num) for num in Efun_Redis.redis_lrange(item, start=start, end=end) ]}]
                elif type == 'db':
                    datas += [{'name':name, 'data':[ float(num.value) for num in db_datas.filter(History_Number.itemid == item).all()]}]
            infos.append({'name':bus.name, 'datas':datas})
        return_jsons['infos'] = infos

    #列表位置返回的内部函数
    def try_list(index):
        try:
            return int(date_list.index(index))
        except:
            return int(date_list.index(strftime_to_date(date_to_strftime(index) + 60)))

    if request.is_xhr and request.method == 'GET':
        try:
            web_range = request.args.get('range')
            web_start = request.args.get('start')
            web_end = request.args.get('end')
            if web_range:
                if web_range == '1h':start = -30
                elif web_range == '2h':start = -60
                elif web_range == '6h':start = -120
                elif web_range == '12h':start = -240
                elif web_range == '1d':start = 0

            elif web_start and web_end:
                #判断查询范围是不是当前的。如果是当天的直接从redis中读取返回
                now_date, web_start, web_end = date_time('%Y-%m-%d'), web_start.encode('utf-8'), web_end.encode('utf-8')
                web_range = u'%s 至 %s' %(web_start, web_end)
                if now_date == web_start.split()[0] and now_date == web_end.split()[0]:
                    date_list = Efun_Redis.redis_lrange(config.time_name)
                    start, end = try_list(web_start), try_list(web_end)
                else:
                    #从数据库中读取。返回到前端页面
                    db_datas = db.session.query(History_Number).filter(History_Number.datetime >=web_start,History_Number.datetime <=web_end)
                    path = request.args.get('path')
                    date_list = [ db_datetime_string(d.datetime, '%Y-%m-%d %H:%M') for d in db_datas.all()]
                    new_date_list = list(set(date_list))
                    new_date_list.sort()
                    return_jsons.update({'datetime':new_date_list})

                    section = db.session.query(Sections).filter(Sections.href == path).first()
                    return_items_datas(section,'db')

                    return jsonify({'code':200, 'message':return_jsons, 'range':web_range})

            else:
                if int(Efun_Redis.redis_len(config.time_name)) > 30:start=-30
                else:start = 0

            if web_range == '1d':
                return_jsons.update({"datetime": Efun_Redis.redis_lrange(config.time_name, start=start, end=end)})
            else:
                return_jsons.update({"datetime":[ d.encode('utf-8').split()[-1] for d in Efun_Redis.redis_lrange(config.time_name, start=start, end=end)]})

            section = db.session.query(Sections).filter(Sections.href.like('%%%s' %url)).first()
            return_items_datas(section)
            if not web_range:web_range='1h'

            return jsonify({'code':200, 'message':return_jsons, 'range':web_range})
        except BaseException,e:
            return jsonify({'code':400, 'message':u'ajax访问错误'})
    else:
        return jsonify({'code':400, 'message':u'访问错误'})




@business.route('/tw_all/pay/')
def tw_all_pay():
    start = '2017-05-19 18:32'
    end = '2017-05-19 19:32'


    abc = db.session.query(History_Number).filter(History_Number.datetime >=start,History_Number.datetime <=end)
    print [ a.datetime for a in abc.all()]

    for a in abc.all():
        print type(a.datetime)

    return 'success'




