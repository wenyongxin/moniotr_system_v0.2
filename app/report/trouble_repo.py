#coding: utf-8

import time,datetime,json,re,calendar,sys
from sqlalchemy import or_
from . import report
from .. import db, csrf
from flask_login import login_required
from .. decorators import user_required
from flask import render_template, flash, redirect, session, url_for, request,Response
from .. models import Sections, Permission_Model, Permission
from .. models import User,Trouble_repo,Trouble_repo_add,Zabbix_group
import export_excel

sys.path.append('../..')
import config



@report.route('/troubleinfo/', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
#故障报告展示
def trouble_report():
    today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    hostgroup_info = Zabbix_group.query.all()
    group_list = []
    for group in hostgroup_info:
        group_name = group.group_name
        try:
            if re.search(u"(^亚欧_|^国内_|^港台_|^韩国_)",group_name):

                if re.search(u"(^韩国_)",group_name):
                    group_name = '韩语-%s' % group_name.split('_')[2]
                elif re.search(u"(^港台_)",group_name):
                    group_name = '繁体-%s' % group_name.split('_')[2]

                elif re.search(u"(^国内_)", group_name):

                    name_list = group_name.split('_')
                    group_name = '%s-%s' % (name_list[(len(name_list) - 1)], name_list[2])
                else:
                    name_list = group_name.split('_')
                    group_name = '%s-%s' % (name_list[(len(name_list)-1)],name_list[2])
        except:
            group_name = group_name

        group_list.append(group_name)


    if request.method == 'POST':
        repo_date = request.form['repo_date']
        repo_type = request.form['repo_type']

        # 日报
        if  repo_type == 'daily':
            if repo_date == today:
                trouble_infos = Trouble_repo.query.filter(or_(Trouble_repo.trouble_date==today,Trouble_repo.trouble_status!=u'完成')).all()
                if trouble_infos:
                    return render_template('report/trouble_tbody.html', trouble_infos=trouble_infos)
                else:
                    msg = u'<tr><td style="color: green;font-size: 30px;" colspan="20"><marquee scrollAmount=15  direction=right>%s 无故障报告!</marquee></td></tr>' % repo_date
                    return Response(msg)
            else:
                trouble_infos = Trouble_repo.query.filter_by(trouble_date=repo_date).all()
                if trouble_infos:
                    return render_template('report/trouble_tbody.html',trouble_infos=trouble_infos)
                else:
                    msg = u'<tr><td style="color: green;font-size: 30px;" colspan="20"><marquee scrollAmount=15  direction=right>%s 无故障报告!</marquee></td></tr>' % repo_date
                    return Response(msg)
        #周报
        else:
            #获取当前日期
            if repo_date:
                b = repo_date.split('-')
                today = int(datetime.datetime(int(b[0]), int(b[1]), int(b[2])).strftime("%w"))
                now = datetime.datetime.strptime(repo_date, '%Y-%m-%d')

            else:
                today = int(datetime.datetime.now().weekday())
                now = datetime.datetime.now()

            #获取上周五
            monday = now + datetime.timedelta(days=-today)

            monday = monday  + datetime.timedelta(days=-2)
            monday = monday.strftime('%Y-%m-%d')

            #获取本周周四日期
            sunday = now + datetime.timedelta(days=+(4 - today))
            sunday = sunday.strftime('%Y-%m-%d')

            #获取本周周一到周日的故障
            trouble_infos = Trouble_repo.query.filter(Trouble_repo.trouble_date.between(monday,sunday)).all()

            if repo_date:
                if trouble_infos:
                    return render_template('report/trouble_tbody.html', trouble_infos=trouble_infos)
                else:
                    msg = u'<tr><td style="color: green;font-size: 30px;" colspan="20"><marquee scrollAmount=15  direction=right>%s 至 %s 无故障报告!</marquee></td></tr>' % (
                        monday, sunday)
                    return Response(msg)

    #默认当天故障报告
    else:
        trouble_add_count = Trouble_repo_add.query.count()
        trouble_add_info = Trouble_repo_add.query.first()
        trouble_infos = Trouble_repo.query.filter(or_(Trouble_repo.trouble_date==today,Trouble_repo.trouble_status!=u'完成')).all()
        sum_core = 0
        sum_ncore = 0
        for trouble in trouble_infos:
            if trouble.isnot_core == u'是':
                try:
                    times = int(trouble.affect_time)
                    sum_core += times
                except:
                    times = trouble.affect_time
            else:
                try:
                    times = int(trouble.affect_time)
                    sum_ncore += times
                except:
                    times = trouble.affect_time
        trouble_times = sum_core
        stab_per = round((1 - float(sum_core) / 1440) * 100, 2)
        trouble_times_1 = sum_ncore
        stab_per_1 = round((1 - float(sum_ncore) / 1440) * 100, 2)


        return render_template('report/trouble_repo.html',**locals())



@report.route('/troubleadd/', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
def trouble_add():
    if request.method == 'POST':
        id = request.form.get('id',None)
        action = request.form.get('action',None)
        trouble_date = request.form.get('trouble_date',None)
        operating_center = request.form.get('operating_center',None)
        business_module = request.form.get('business_module',None)
        trouble_affair = request.form.get('trouble_affair',None)
        affect_scope = request.form.get('affect_scope',None)
        isnot_inner = request.form.get('isnot_inner',None)
        affect_time = request.form.get('affect_time',None)
        isnot_experience = request.form.get('isnot_experience',None)
        affect_user = request.form.get('affect_user',None)
        affect_money = request.form.get('affect_money',None)
        data_source = request.form.get('data_source',None)
        isnot_core = request.form.get('isnot_core',None)
        trouble_type = request.form.get('trouble_type',None)
        heading_user = request.form.get('heading_user',None)
        trouble_attr = request.form.get('trouble_attr',None)
        trouble_status = request.form.get('trouble_status',None)
        trouble_cause = request.form.get('trouble_cause',None)
        whith_process = request.form.get('whith_process',None)
        lesson_course = request.form.get('lesson_course',None)
        improve = request.form.get('improve',None)

        if id:
            if action == 'change_trouble':
                ch_info = Trouble_repo.query.filter_by(id=id).first()

                ch_info.trouble_date=trouble_date
                ch_info.operating_center=operating_center
                ch_info.business_module=business_module
                ch_info.trouble_affair=trouble_affair
                ch_info.affect_scope=affect_scope
                ch_info.isnot_inner=isnot_inner
                ch_info.affect_time=affect_time
                ch_info.isnot_experience=isnot_experience
                ch_info.affect_user=affect_user
                ch_info.affect_money=affect_money
                ch_info.data_source=data_source
                ch_info.isnot_core=isnot_core
                ch_info.trouble_type=trouble_type
                ch_info.heading_user=heading_user
                ch_info.trouble_attr=trouble_attr
                ch_info.trouble_status=trouble_status
                ch_info.trouble_cause=trouble_cause
                ch_info.whith_process=whith_process
                ch_info.lesson_course=lesson_course
                ch_info.improve=improve
                db.session.add(ch_info)
                db.session.commit()
                return Response('更新成功!')

            if action == 'publish_trouble':
                info = Trouble_repo(trouble_date=trouble_date, operating_center=operating_center,
                     business_module=business_module,
                     trouble_affair=trouble_affair, affect_scope=affect_scope,
                     isnot_inner=isnot_inner,
                     affect_time=affect_time, isnot_experience=isnot_experience,
                     affect_user=affect_user,
                     affect_money=affect_money, data_source=data_source, isnot_core=isnot_core,
                     trouble_type=trouble_type,
                     heading_user=heading_user, trouble_attr=trouble_attr,
                     trouble_status=trouble_status, trouble_cause=trouble_cause,
                     whith_process=whith_process, lesson_course=lesson_course, improve=improve)
                db.session.add(info)
                db.session.commit()


                del_info = Trouble_repo_add.query.filter_by(id=id).first()
                db.session.delete(del_info)
                db.session.commit()
                return Response('发布成功!')

            if action == 'del_trouble':
                try:
                    del_info = Trouble_repo_add.query.filter_by(id=id).first()
                    db.session.delete(del_info)
                    db.session.commit()
                    return Response('删除成功!')
                except:
                    del_info = Trouble_repo.query.filter_by(id=id).first()

                    db.session.delete(del_info)
                    db.session.commit()
                    return Response('删除成功!')

            if action == 'alter_trouble':
                info = Trouble_repo_add.query.filter_by(id=id)

                info.update({'trouble_date':trouble_date,'operating_center':operating_center,'business_module':business_module,
                 'trouble_affair':trouble_affair,'affect_scope':affect_scope,'isnot_inner':isnot_inner,
                 'affect_time':affect_time,'isnot_experience':isnot_experience,'affect_user':affect_user,
                 'affect_money':affect_money,'data_source':data_source,'isnot_core':isnot_core,'trouble_type':trouble_type,
                 'heading_user':heading_user,'trouble_attr':trouble_attr,'trouble_status':trouble_status,'trouble_cause':trouble_cause,
                 'whith_process':whith_process,'lesson_course':lesson_course,'improve':improve})
                db.session.commit()
                return Response('保存成功!')


        else:
            if action == 'add_trouble':
                info = Trouble_repo_add(trouble_date=trouble_date,operating_center=operating_center,business_module=business_module,
                     trouble_affair=trouble_affair,affect_scope=affect_scope,isnot_inner=isnot_inner,
                     affect_time=affect_time,isnot_experience=isnot_experience,affect_user=affect_user,
                     affect_money=affect_money,data_source=data_source,isnot_core=isnot_core,trouble_type=trouble_type,
                     heading_user=heading_user,trouble_attr=trouble_attr,trouble_status=trouble_status,trouble_cause=trouble_cause,
                     whith_process=whith_process,lesson_course=lesson_course,improve=improve)
                db.session.add(info)
                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                return Response('添加成功！')



@report.route('/exporttrouble/', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
def troble_export():
    repo_date = request.form.get('repo_date')
    repo_type = request.form.get('repo_type')
    trouble_times = str(request.form.get('trouble_times'))
    stab_per = str(request.form.get('stab_per'))
    trouble_times_1 = str(request.form.get('trouble_times_1'))
    stab_per_1 = str(request.form.get('stab_per_1'))
    if  repo_type == 'daily':
        trouble_infos = Trouble_repo.query.filter_by(trouble_date=repo_date).all()
        trouble_list = []
        for i in trouble_infos:
            List = [i.trouble_date,i.operating_center,i.business_module,i.trouble_affair,i.affect_scope,i.isnot_inner,i.affect_time,i.isnot_experience,i.affect_user,i.affect_money,
                    i.data_source,i.isnot_core,i.trouble_type,i.heading_user,i.trouble_attr,i.trouble_status,i.trouble_cause,i.whith_process,i.lesson_course,i.improve]

            trouble_list.append(List)

        name = u'故障报告%s.xlsx' % repo_date
        title = u'%s/app/static/files/report/%s' % (config.basedir,name)
        head = u'故障日报'
        export_excel.trouble(trouble_times, stab_per,trouble_times_1,stab_per_1,trouble_list,title,head)
        return Response(r'http://%s/static/files/report/%s' % (request.host,name))

    else:
        b = repo_date.split('-')
        today = int(datetime.datetime(int(b[0]),int(b[1]),int(b[2])).strftime("%w"))
        now =  datetime.datetime.strptime(repo_date,'%Y-%m-%d')


        # 获取上周五
        monday = now + datetime.timedelta(days=-today)
        monday = monday + datetime.timedelta(days=-2)
        monday = monday.strftime('%Y-%m-%d')

        # 获取本周周四日期
        sunday = now + datetime.timedelta(days=+(4 - today))
        sunday = sunday.strftime('%Y-%m-%d')



        trouble_infos = Trouble_repo.query.filter(Trouble_repo.trouble_date.between(monday,sunday)).order_by('trouble_date').all()
        trouble_list = []
        for i in trouble_infos:
            List = [i.trouble_date,i.operating_center,i.business_module,i.trouble_affair,i.affect_scope,i.isnot_inner,i.affect_time,i.isnot_experience,i.affect_user,i.affect_money,
                    i.data_source,i.isnot_core,i.trouble_type,i.heading_user,i.trouble_attr,i.trouble_status,i.trouble_cause,i.whith_process,i.lesson_course,i.improve]
            trouble_list.append(List)

        name = u'周故障报告%s-%s.xlsx' % (monday,sunday)
        title = u'%s/app/static/files/report/%s' % (config.basedir,name)
        head = u'故障周报'
        export_excel.trouble(trouble_times, stab_per, trouble_times_1, stab_per_1, trouble_list, title, head)

        return Response(r'http://%s/static/files/report/%s' % (request.host,name))


