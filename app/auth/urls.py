#!/usr/bin/env python
#ecoding:utf-8

'''
功能：
可以对页面进行url路径的管理。实现了增删改功能，能够修改图标
'''


from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from . import auth
from .. import db
from ..models import Sections, Icon
from ..scripts.tools import save_db,delete_db
from ..decorators import admin_required

@auth.before_request
def get_browser():
    # print request.user_agent
    if "chrome" not in  request.user_agent.browser:
        return '''<h1>访问错误 本系统只支持谷歌浏览器，
                        <a href="http://sw.bos.baidu.com/sw-search-sp/software/ba34c905dbdd4/ChromeStandalone_57.0.2987.98_Setup.exe">谷歌下载地址</a>
                </h1><hr><h3>监控团队</h3>'''



#管理url路径
@auth.route('/manager_url')
@login_required
@admin_required
def manager_url():
    html_data = {
        'name':u'版块管理',
        'sections_db':current_user.sesctions(current_user.permission_id),
        'heads': db.session.query(Sections).filter(Sections.head==1).all()
    }

    return render_template('manager/manager_url.html', **html_data)



#修改url信息
@auth.route('/manager_edit', methods=['GET','POST'])
@login_required
@admin_required
def edit_url():
    if request.method == 'POST':
        datas = { key:value[0].encode("utf-8") for key,value in dict(request.form).items()}
        #判断是否为修改还是创建
        icon = Icon.query.filter_by(icon_name = datas['section_icon']).first()
        if datas['sesction_id'] == 'clone' or datas['sesction_id'] == 'create':
            #执行创建命令
            try:
                sesction = Sections(icon_id = icon.id,name = datas['sesction_name'],
                                href = datas['sesction_href'],membership = int(datas['section_head']),
                                describe = datas['section_describe'])
            except:
                sesction = Sections(icon_id = icon.id,name = datas['sesction_name'],href = datas['sesction_href'],
                                    head = 1)
            try:
                save_db(sesction)
                flash({'type':'ok','message':u'添加成功'})
            except:
                flash({'type':'error','message':u'不能重复添加'})

        else:
            find_id = db.session.query(Sections).filter(Sections.id == datas['sesction_id']).first()
            if find_id:
                #开始修改
                find_id.name = datas['sesction_name']
                find_id.href = datas['sesction_href']
                find_id.icon_id = icon.id
                try:
                    find_id.membership = datas['section_head']
                    find_id.describe = datas['section_describe']
                except:pass
                save_db(find_id)
                flash({'type':'ok','message':u'修改完成'})
        return redirect(url_for('auth.manager_url'))
    else:
        # 获取隶属信息
        heads = db.session.query(Sections).filter(Sections.head==1).all()
        id = request.args.get('id')
        if id:
            info = db.session.query(Sections).filter(Sections.id == int(id)).first()
        else:
            info = False
        return render_template('manager/alert_edit.html', info=info, heads=heads)


#删除url信息
@auth.route('/manager_delete', methods=['GET'])
@login_required
@admin_required
def delte_url():
    id = request.args.get('id')
    #查找sesction的id信息
    find_id = db.session.query(Sections).filter(Sections.id == id).first()
    #确认head下是否包含url信息
    find_this_head = db.session.query(Sections).filter(Sections.membership == id).first()
    if find_this_head:
        flash({'type':'error','message':u'一级目标不为空'})
    else:
        try:
            delete_db(find_id)
            flash({'type':'ok','message':u'删除成功'})
        except BaseException,e:
            flash({'type':'error','message':u'删除失败'})
    return redirect(url_for('auth.manager_url'))