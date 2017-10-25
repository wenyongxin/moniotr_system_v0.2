#coding: utf-8

import time,datetime,json,re,calendar,sys

from . import report
from .. import db, csrf
from flask_login import login_required
from .. decorators import user_required
from flask import render_template, flash, redirect, session, url_for, request,Response
from .. models import Sections, Permission_Model, Permission
from .. models import User,Trouble_repo,Trouble_repo_add,Month_trouble_repo,Month_trouble_log,Anomaly_log,Zabbix_group
import export_excel

sys.path.append('../..')
import config



@report.route('/anomalyrecord/', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
#异常记录主页
def anomaly_record():
    today = datetime.date.today()
    hostgroup_info = Zabbix_group.query.all()
    group_list = []
    for group in hostgroup_info:
        group_name = group.group_name
        if re.search(u"(^亚欧_|^国内_|^港台_|^韩国_)", group_name):
            try:
                if re.search(u"(^韩国_)", group_name):
                    group_name = '韩语-%s' % group_name.split('_')[2]
                elif re.search(u"(^港台_)", group_name):
                    group_name = '繁体-%s' % group_name.split('_')[2]
                elif re.search(u"(^国内_)", group_name):
                    name_list = group_name.split('_')
                    group_name = '%s-%s' % (name_list[(len(name_list) - 1)], name_list[2])
                else:
                    name_list = group_name.split('_')
                    group_name = '%s-%s' % (name_list[(len(name_list) - 1)], name_list[2])
            except:
                group_name = group_name
        else:
            pass
        group_list.append(group_name)

    yesterday = (today - datetime.timedelta(0)).strftime('%Y-%m-%d')

    anomaly_infos = Anomaly_log.query.filter(Anomaly_log.occurrence_time.ilike("%s%%" % yesterday)).all()

    return render_template('report/anomaly.html',**locals())


@report.route('/anomalyreq/', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
#异常记录增删改查
def anomaly_request():
    #当天日期
    today = datetime.date.today().strftime('%Y-%m-%d')
    if request.method == 'POST':
        anomaly_date = request.form.get('anomaly_date',None)
        repo_type = request.form.get('repo_type', None)

        #查（仅查询携带anomaly_date参数）
        if anomaly_date:
            #获取查询时间的所有异常记录
            if repo_type =="daily":
                anomaly_infos = Anomaly_log.query.filter(Anomaly_log.occurrence_time.ilike("%s%%" % anomaly_date)).all()
            elif repo_type =="weeken":
                # 获取当前日期

                if anomaly_date:
                    b = anomaly_date.split('-')
                    today = int(datetime.datetime(int(b[0]), int(b[1]), int(b[2])).strftime("%w"))
                    now = datetime.datetime.strptime(anomaly_date, '%Y-%m-%d')

                else:
                    today = int(datetime.datetime.now().weekday())
                    now = datetime.datetime.now()

                # 获取上周五
                monday = now + datetime.timedelta(days=-today)

                monday = monday + datetime.timedelta(days=-2)
                monday = monday.strftime('%Y-%m-%d')



                # 获取本周周四日期
                sunday = now + datetime.timedelta(days=+(4 - today))
                sunday = sunday.strftime('%Y-%m-%d')
                # 获取本周周一到周日的故障
                anomaly_infos = Anomaly_log.query.filter(Anomaly_log.occurrence_time.between(monday+" 00:00", sunday+" 23:59")).all()

                print anomaly_infos

            elif repo_type == "month":
                days = str(anomaly_date).split("-")
                day = days[0]+'-'+days[1]
                anomaly_infos = Anomaly_log.query.filter(Anomaly_log.occurrence_time.ilike("%s-%%" % day)).all()
            data_list = []
            for i in anomaly_infos:
                data = {}
                data['id'] = i.id
                data['anomaly_affair'] = i.anomaly_affair
                data['oper_center'] = i.oper_center
                data['business_module'] = i.business_module
                data['anomaly_source'] = i.anomaly_source
                data['anomaly_type'] = i.anomaly_type
                data['anomaly_level'] = i.anomaly_level
                data['isnot_fake'] = i.isnot_fake
                data['isnot_maintain'] = i.isnot_maintain
                data['isnot_affect'] = i.isnot_affect
                data['occurrence_time'] = i.occurrence_time
                data['error_time'] = i.error_time
                data['processing_stime'] = i.processing_stime
                data['processing_etime'] = i.processing_etime
                data['processing_ltime'] = i.processing_ltime
                data['anomaly_attr'] = i.anomaly_attr
                data['processor'] = i.processor
                data['result'] = i.result
                data['five_minutes'] = i.five_minutes
                data['fifteen_minutes'] = i.fifteen_minutes
                data['thirty_minutes'] = i.thirty_minutes
                data['an_hour'] = i.an_hour
                data['two_hours'] = i.two_hours
                data['evaluation'] = i.evaluation
                data['monitor_follow_people'] = i.monitor_follow_people
                data_list.append(data)
            data_list = json.dumps(data_list)

            return data_list
        else:
            id = request.form.get('id',None)
            action = request.form.get('action', None)
            #删（只有删除携带action参数）
            if action:
                anomaly = Anomaly_log.query.filter_by(id=id).first()
                db.session.delete(anomaly)
                db.session.commit()
                return Response('删除成功!')
            else:
                anomaly_affair = request.form.get('anomaly_affair',None)
                oper_center = request.form.get('oper_center',None)
                anomaly_source = request.form.get('anomaly_source',None)
                anomaly_type = request.form.get('anomaly_type',None)
                business_module = request.form.get('business_module',None)
                anomaly_level = request.form.get('anomaly_level',None)
                isnot_fake = request.form.get('isnot_fake',None)
                isnot_maintain = request.form.get('isnot_maintain',None)
                isnot_affect = request.form.get('isnot_affect',None)
                occurrence_time = request.form.get('occurrence_time',today)
                error_time = request.form.get('error_time',today)
                processing_stime = request.form.get('processing_stime',today)
                processing_etime = request.form.get('processing_etime',today)
                try:
                    processing_ltime = ((datetime.datetime.strptime(request.form.get('processing_etime'),'%Y-%m-%d %H:%M') - datetime.datetime.strptime(request.form.get('processing_stime'), '%Y-%m-%d %H:%M')).seconds / 60)
                except:
                    processing_ltime = 0
                anomaly_attr = request.form.get('anomaly_attr',None)
                processor = request.form.get('processor',None)
                result = request.form.get('result',None)
                five_minutes = request.form.get('five_minutes',None)
                fifteen_minutes = request.form.get('fifteen_minutes',None)
                thirty_minutes = request.form.get('thirty_minutes',None)
                an_hour = request.form.get('an_hour',None)
                two_hours = request.form.get('two_hours',None)
                evaluation = request.form.get('evaluation',None)
                monitor_follow_people = request.form.get('monitor_follow_people',None)
                #改（增加修改仅修改携带id参数）
                if id:
                    anomaly = Anomaly_log.query.filter_by(id=id).first()
                    anomaly.anomaly_affair = anomaly_affair
                    anomaly.oper_center = oper_center
                    anomaly.anomaly_source = anomaly_source
                    anomaly.anomaly_type = anomaly_type
                    anomaly.business_module = business_module
                    anomaly.anomaly_level = anomaly_level
                    anomaly.isnot_fake = isnot_fake
                    anomaly.isnot_maintain = isnot_maintain
                    anomaly.isnot_affect = isnot_affect
                    anomaly.occurrence_time = occurrence_time
                    anomaly.error_time = error_time
                    anomaly.processing_stime = processing_stime
                    anomaly.processing_etime = processing_etime
                    anomaly.processing_ltime = processing_ltime
                    anomaly.anomaly_attr = anomaly_attr
                    anomaly.processor = processor
                    anomaly.result = result
                    anomaly.five_minutes = five_minutes
                    anomaly.fifteen_minutes = fifteen_minutes
                    anomaly.thirty_minutes = thirty_minutes
                    anomaly.an_hour = an_hour
                    anomaly.two_hours = two_hours
                    anomaly.evaluation = evaluation
                    anomaly.monitor_follow_people = monitor_follow_people
                    db.session.add(anomaly)
                    db.session.commit()
                    return Response('修改成功!')
                #增（无id参数）
                else:
                    info = Anomaly_log(
                    anomaly_affair=anomaly_affair,
                    oper_center=oper_center,
                    anomaly_source=anomaly_source,
                    anomaly_type=anomaly_type,
                    business_module=business_module,
                    anomaly_level=anomaly_level,
                    isnot_fake=isnot_fake,
                    isnot_maintain=isnot_maintain,
                    isnot_affect=isnot_affect,
                    occurrence_time=occurrence_time,
                    error_time=error_time,
                    processing_stime=processing_stime,
                    processing_etime=processing_etime,
                    processing_ltime =processing_ltime,
                    anomaly_attr=anomaly_attr,
                    processor=processor,
                    result=result,
                    five_minutes=five_minutes,
                    fifteen_minutes=fifteen_minutes,
                    thirty_minutes=thirty_minutes,
                    an_hour=an_hour,
                    two_hours=two_hours,
                    evaluation=evaluation,
                    monitor_follow_people=monitor_follow_people,
                    )
                    db.session.add(info)
                    db.session.commit()
                    return Response('添加成功!')
    else:
        return Response('无任何操作！')


@report.route('/exportanomaly/', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
#导出异常记录
def anomaly_export():
    anomaly_date = request.form.get('anomaly_date', None)
    repo_type = request.form.get('repo_type', None)
    if anomaly_date:
        if repo_type == "daily":
            anomaly_infos = Anomaly_log.query.filter(Anomaly_log.occurrence_time.ilike("%s%%" % anomaly_date)).all()
            name = u'异常记录%s.xlsx' % anomaly_date
        elif repo_type == "weeken":
            # 获取当前日期

            if anomaly_date:
                b = anomaly_date.split('-')
                today = int(datetime.datetime(int(b[0]), int(b[1]), int(b[2])).strftime("%w"))
                now = datetime.datetime.strptime(anomaly_date, '%Y-%m-%d')

            else:
                today = int(datetime.datetime.now().weekday())
                now = datetime.datetime.now()

            # 获取上周五
            monday = now + datetime.timedelta(days=-today)

            monday = monday + datetime.timedelta(days=-2)
            monday = monday.strftime('%Y-%m-%d')

            # 获取本周周四日期
            sunday = now + datetime.timedelta(days=+(4 - today))
            sunday = sunday.strftime('%Y-%m-%d')
            # 获取本周周一到周日的故障
            anomaly_infos = Anomaly_log.query.filter(
                Anomaly_log.occurrence_time.between(monday + " 00:00", sunday + " 23:59")).all()

            name = u'异常记录%s-%s.xlsx' % (monday,sunday)

        elif repo_type == "month":
            days = str(anomaly_date).split("-")
            day = days[0] + '-' + days[1]
            name = u'异常记录%s月.xlsx' % day
            anomaly_infos = Anomaly_log.query.filter(Anomaly_log.occurrence_time.ilike("%s-%%" % day)).all()

        anomaly_list = []
        for i in anomaly_infos:
            List = [
                    i.anomaly_affair,
                    i.oper_center ,
                    i.anomaly_source,
                    i.anomaly_type,
                    i.business_module,
                    i.anomaly_level,
                    i.isnot_fake,
                    i.isnot_maintain,
                    i.isnot_affect,
                    i.occurrence_time,
                    i.error_time,
                    i.processing_stime,
                    i.processing_etime,
                    i.anomaly_attr ,
                    i.processor ,
                    i.result,
                    i.five_minutes,
                    i.fifteen_minutes,
                    i.thirty_minutes,
                    i.an_hour,
                    i.two_hours,
                    i.evaluation,
                    i.monitor_follow_people
                    ]
            anomaly_list.append(List)

        title = u'%s/app/static/files/report/%s' % (config.basedir, name)
        export_excel.anomaly(anomaly_list,title)
        return Response(r'http://%s/static/files/report/%s' % (request.host, name))
    else:
        return Response('导出失败!')




@report.route('/alteranomaly/', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
def alter_anomaly():
    id = request.form.get('id', None)
    if id:
        try:
            anomaly_infos = Anomaly_log.query.filter_by(id=id).all()
            data_list = []
            for i in anomaly_infos:
                data = {}
                data['id'] = i.id
                data['anomaly_affair'] = i.anomaly_affair
                data['oper_center'] = i.oper_center
                data['business_module'] = i.business_module
                data['anomaly_source'] = i.anomaly_source
                data['anomaly_type'] = i.anomaly_type
                data['anomaly_level'] = i.anomaly_level
                data['isnot_fake'] = i.isnot_fake
                data['isnot_maintain'] = i.isnot_maintain
                data['isnot_affect'] = i.isnot_affect
                data['occurrence_time'] = i.occurrence_time
                data['error_time'] = i.error_time
                data['processing_stime'] = i.processing_stime
                data['processing_etime'] = i.processing_etime
                data['processing_ltime'] = i.processing_ltime
                data['anomaly_attr'] = i.anomaly_attr
                data['processor'] = i.processor
                data['result'] = i.result
                data['five_minutes'] = i.five_minutes
                data['fifteen_minutes'] = i.fifteen_minutes
                data['thirty_minutes'] = i.thirty_minutes
                data['an_hour'] = i.an_hour
                data['two_hours'] = i.two_hours
                data['evaluation'] = i.evaluation
                data['monitor_follow_people'] = i.monitor_follow_people
                data_list.append(data)
            data_list = json.dumps(data_list)
            return data_list
        except:
            return Response('该记录不存在！')
    else:
        return Response('找不到该记录！')