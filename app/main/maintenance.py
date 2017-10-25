#coding: utf-8

import time,datetime,json,re,calendar,sys
from sqlalchemy import or_
from app.main import main
from app import db, csrf
from flask_login import login_required
from app.decorators import user_required
from flask import render_template, flash, redirect, session, url_for, request,Response
from app.models import Sections, Permission_Model, Permission,Maintenance,Zabbix_group
from ..scripts.zabbix import Efun_Zabbix
from app.scripts.tools import delete_dbs

zabbix = Efun_Zabbix()



@main.route('/maintenance', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
#故障报告展示
def maintenance():
    now = time.time()
    maintenance_info = Maintenance.query.all()
    data_list = []
    N = 0
    for i in maintenance_info:
        id=i.id
        main_id = i.main_id
        group_name = i.group_name
        main_type = i.main_type
        start_time = i.start_time
        end_time = i.end_time
        main_info = i.main_info

        #字符串格式时间转化为时间戳
        stime = time.strptime(start_time,'%Y-%m-%d %H:%M')
        etime = time.strptime(end_time,'%Y-%m-%d %H:%M')
        stime = time.mktime(stime)
        etime = time.mktime(etime)

        if stime < now < etime:
            main_status = u'维护中'
        elif now > etime:
            main_status = u'已过期'
        else:
            main_status = u'未进行'


        main_dit = {'id':id,'main_id':main_id,'main_type':main_type,'start_time':start_time,
             'main_info':main_info,'end_time':end_time,'group_name':group_name,'main_status':main_status}
        if main_type == u'日常维护':
            if main_status == u'维护中':
                data_list.insert(0,main_dit)
                N += 1
            else:
                if main_status == u'未进行':
                    data_list.insert(N, main_dit)
                    N += 1
                else:
                    data_list.insert(N, main_dit)

        else:
            data_list.append(main_dit)

    hostgroup_info = Zabbix_group.query.all()

    return render_template('maintenance.html',**locals())
    return 'success'



@main.route('/createmain', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
def create_maintenance():
    ID = request.form.get('ID', None)
    main_info = request.form.get('main_info', None)
    start_time = request.form.get('start_time', None)
    end_time = request.form.get('end_time', None)
    groupid = request.form.get('groupid', None)
    main_type = int(request.form.get('main_type', 0))
    every = int(request.form.get('every', 1))
    main_day = int(request.form.get('main_day', 0))
    stime = request.form.get('stime', None)
    ltime = request.form.get('ltime', None)


    if ID:
        main = Maintenance.query.filter_by(id=ID).first()
        main_id = main.main_id

        db.session.delete(main)
        db.session.commit()
        params = [main_id]
        method = "maintenance.delete"
        result = zabbix.get_api_data(params, method)

    else:
        pass


    if main_info and start_time and end_time and groupid:
        groupids = groupid.strip(',').split(',')

        SinceArray = time.strptime(start_time, "%Y-%m-%d %H:%M")
        timeSince = int(time.mktime(SinceArray)) - 600  # - 28800

        EndArray = time.strptime(end_time, "%Y-%m-%d %H:%M")
        timeEnd = int(time.mktime(EndArray)) + 600  # - 28800


        if main_type == 0:
            ltime = timeEnd - timeSince
            stime = 0
            main_day = 0
        else:
            stime = int(stime.split(':')[0]) * 60*60 + int(stime.split(':')[1])*60
            ltime = int(ltime)*60

        params = {
            "name": main_info,
            "description": main_info,
            "active_since": timeSince,
            "active_till": timeEnd,
            "groupids": groupids,
            "timeperiods": [
                {
                    "timeperiod_type": main_type,
                    "every": every,
                    "dayofweek": main_day,
                    "start_date": timeSince,
                    'start_time':stime,
                    "period": ltime,
                }
            ]
        }
        method = "maintenance.create"
        try:
            result = zabbix.get_api_data(params, method)

            maintenance_type = {0: u'日常维护', 2: u'周期维护(天)', 3: u'周期维护(周)', 4: u'周期维护(月)'}
            mainid = result['maintenanceids'][0]

            group_id = groupids[0]
            group_name = Zabbix_group.query.filter_by(group_id=group_id).first()
            if group_name:
                 group_name = group_name.group_name
            else:
                group_name = 'Unknown'
            main_add = Maintenance(group_name=group_name,main_info=main_info,main_id=mainid,start_time=start_time,end_time=end_time,main_type=maintenance_type[main_type])
            db.session.add(main_add)
            db.session.commit()


            return Response('')
        except Exception,e:
            return Response('该维护信息已存在!')

    else:
        return Response(u'请输入完整信息')

    ID = request.form.get('ID', None)
    main_info = request.form.get('main_info', None)
    start_time = request.form.get('start_time', None)
    end_time = request.form.get('end_time', None)
    groupid = request.form.get('groupid', None)
    main_type = int(request.form.get('main_type', 0))
    every = int(request.form.get('every', 1))
    main_day = int(request.form.get('main_day', 0))
    stime = request.form.get('stime', None)
    ltime = request.form.get('ltime', None)

    if ID:
        main = Maintenance.query.filter_by(id=ID).first()
        main_id = main.main_id

        db.session.delete(main)
        db.session.commit()
        params = [main_id]
        method = "maintenance.delete"
        result = zabbix.get_api_data(params, method)

    else:
        pass


    if main_info and start_time and end_time and groupid:
        groupids = groupid.strip(',').split(',')

        SinceArray = time.strptime(start_time, "%Y-%m-%d %H:%M")
        timeSince = int(time.mktime(SinceArray)) - 600  # - 28800

        EndArray = time.strptime(end_time, "%Y-%m-%d %H:%M")

        timeEnd = int(time.mktime(EndArray)) + 600  # - 28800

        if main_type == 0:
            ltime = timeEnd - timeSince
            stime = 0
            main_day = 0
        else:
            stime = int(stime.split(':')[0]) * 60*60 + int(stime.split(':')[1])*60
            ltime = int(ltime)*60

        params = {
            "name": main_info,
            "description": main_info,
            "active_since": timeSince,
            "active_till": timeEnd,
            "groupids": groupids,
            "timeperiods": [
                {
                    "timeperiod_type": main_type,
                    "every": every,
                    "dayofweek": main_day,
                    "start_date": timeSince,
                    'start_time':stime,
                    "period": ltime,
                }
            ]
        }
        method = "maintenance.create"
        try:
            result = get_api_data(a, params, method)

            maintenance_type = {0: u'日常维护', 2: u'周期维护(天)', 3: u'周期维护(周)', 4: u'周期维护(月)'}
            mainid = result['maintenanceids'][0]

            group_id = groupids[0]
            group_name = Zabbix_group.query.filter_by(group_id=group_id).first()
            if group_name:
                 group_name = group_name.group_name
            else:
                group_name = 'Unknown'
            main_add = Maintenance(group_name=group_name,main_info=main_info,main_id=mainid,start_time=start_time,end_time=end_time,main_type=maintenance_type[main_type])
            db.session.add(main_add)
            db.session.commit()


            return Response('')
        except Exception,e:
            return Response('该维护信息已存在!')

    else:
        return Response(u'请输入完整信息')




@main.route('/getmain', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
def get_main():
    del_data = Maintenance.query.all()
    del_group =  Zabbix_group.query.all()
    delete_dbs(del_data)
    delete_dbs(del_group)


    params_hostgroup = {
        "output": ['groupid', 'name'],
    }
    method_hostgroup = 'hostgroup.get'


    hostgroup_info = zabbix.get_api_data(params_hostgroup, method_hostgroup)

    for i in  hostgroup_info:
        groupname = i['name']
        groupid = i['groupid']
        group_add = Zabbix_group(group_name=groupname,group_id=groupid)
        db.session.add(group_add)
    db.session.commit()





    maintenance_type = {'0': u'日常维护', '2': u'周期维护(天)', '3': u'周期维护(周)', '4': u'周期维护(月)'}
    params_main_get = {
        "output": ['maintenanceid', 'name', 'maintenance_type', 'active_since', 'active_till'],
        "selectGroups": ['groupid', 'name'],
        "selectTimeperiods": "extend",
        "selectHosts": ['hostid', 'name'],
    }

    method_main_get = "maintenance.get"

    maintenance_info = zabbix.get_api_data(params_main_get, method_main_get)

    for i in maintenance_info:
        try:
            group_name = i['groups'][0]['name']
        except:
            group_name = i['hosts'][0]['name']
        main_info = i['name']
        mainid = i['maintenanceid']
        main_type = maintenance_type[i['timeperiods'][0]['timeperiod_type']]
        start_time = float(i['active_since'])
        end_time = float(i['active_till'])

        start_time = time.localtime(start_time)

        start_time = time.strftime('%Y-%m-%d %H:%M', start_time)

        end_time = time.localtime(end_time)
        end_time = time.strftime('%Y-%m-%d %H:%M', end_time)

        main_add = Maintenance(group_name=group_name, main_info=main_info, main_id=mainid, start_time=start_time,
                               end_time=end_time, main_type=main_type)
        db.session.add(main_add)
    db.session.commit()
    return Response('已同步')


    del_data = Maintenance.query.all()
    del_group =  Zabbix_group.query.all()
    delete_dbs(del_data)
    delete_dbs(del_group)


    params_hostgroup = {
        "output": ['groupid', 'name'],
    }
    method_hostgroup = 'hostgroup.get'


    hostgroup_info = zabbix.get_api_data(params_hostgroup, method_hostgroup)

    for i in  hostgroup_info:
        groupname = i['name']
        groupid = i['groupid']
        group_add = Zabbix_group(group_name=groupname,group_id=groupid)
        db.session.add(group_add)
    db.session.commit()


    maintenance_type = {'0': u'日常维护', '2': u'周期维护(天)', '3': u'周期维护(周)', '4': u'周期维护(月)'}
    params_main_get = {
        "output": ['maintenanceid', 'name', 'maintenance_type', 'active_since', 'active_till'],
        "selectGroups": ['groupid', 'name'],
        "selectTimeperiods": "extend",
        "selectHosts": ['hostid', 'name'],
    }

    method_main_get = "maintenance.get"

    maintenance_info = zabbix.get_api_data(params_main_get, method_main_get)


    for i in maintenance_info:
        try:
            group_name = i['groups'][0]['name']
        except:
            if i['hosts']:
                group_name = i['hosts'][0]['name']
            else:
                group_name = "unknown"


        main_info = i['name']
        mainid = i['maintenanceid']
        main_type = maintenance_type[i['timeperiods'][0]['timeperiod_type']]
        start_time = float(i['active_since'])
        end_time = float(i['active_till'])

        start_time = time.localtime(start_time)

        start_time = time.strftime('%Y-%m-%d %H:%M', start_time)

        end_time = time.localtime(end_time)
        end_time = time.strftime('%Y-%m-%d %H:%M', end_time)

        main_add = Maintenance(group_name=group_name, main_info=main_info, main_id=mainid, start_time=start_time,
                               end_time=end_time, main_type=main_type)
        db.session.add(main_add)
    db.session.commit()
    return Response('已同步')






