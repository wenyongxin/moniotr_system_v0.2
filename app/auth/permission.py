#!/usr/bin/env python
#ecoding:utf-8

'''
用于权限模块的管理
能够针对不用的使用需求，定制显示的内容。并加以控制
'''

from flask import render_template, request, flash, jsonify
from flask_login import login_required
from . import auth
from .. import db, csrf
from ..models import Sections, Permission_Model, Permission
from ..scripts.tools import save_db,delete_db,save_many_to_many
from ..decorators import admin_required, permission_required
import json
from func import return_checks





#url访问权限管理
#这里的权限管理只针对具有user权限则，管理员权限的则全部可见。可处理
@auth.route('/manager_permission', methods=['GET','POST'])
@login_required
@admin_required
# @permission_required(Permission.user, path='/manager_permission', app='auth')
def manager_permission():
    html_data = {
        'name':u'权限管理',
        'sections_db':Permission_Model.query.all()
    }
    return render_template('manager/manager_permission.html', **html_data)


#更新权限
@auth.route('/permission_update', methods=['POST','GET'])
@login_required
@admin_required
@csrf.exempt
def permission_update():
    if request.is_xhr:
        #1 判断id的的值，如果是clone或create则创建，如果是id则修改
        #2 返回正确的id 判断是否能从数据库中找到
        #3 判断true的状态数量是否发生过变化
        #4 判断名称是否有变化
        #5 将新选择的版块id加入到new_checked列表中
        id = request.form.get('id')
        newname = request.form.get('newname')
        newdesc = request.form.get('newdesc')
        web_check_info = json.loads(request.form.get('chckboxinfo'))
        new_checked = []
        if id == 'clone':
            #1 先在数据库里创建
            try:
                permission_model = Permission_Model(name = newname, describe = newdesc)
                save_db(permission_model)
                find_id = Permission_Model.query.filter_by(name = newname).first()
                for key_id, value_status in web_check_info.items():
                    if value_status == 'true':
                        new_checked.append(int(key_id))
                save_many_to_many(Sections, find_id, new_checked)
                flash({'type':'ok','message':u'更新成功'})
            except:
                flash({'type':'error','message':u'不能重复'})


        else:
            source_check_info = return_checks(id, True)
            find_id = Permission_Model.query.filter_by(id = id).first()
            if find_id:
                #如果web的选项比数据库中多。则增加
                if int(web_check_info.values().count('true')) > int(source_check_info.values().count('true')):
                    for key_id, value_status in web_check_info.items():
                        if source_check_info.get(int(key_id)) != value_status:
                            new_checked.append(int(key_id))
                    save_many_to_many(Sections, find_id, new_checked)
                #如果web的选项比数据库中少。则减去
                elif int(web_check_info.values().count('true')) < int(source_check_info.values().count('true')):
                    for key_id, value_status in source_check_info.items():
                        if web_check_info.get(u'%s' %key_id) != value_status:
                            new_checked.append(key_id)
                    save_many_to_many(Sections, find_id, new_checked, action='remove')
                if find_id.name != newname or find_id.describe != newdesc:
                    find_id.name = newname
                    find_id.describe = newdesc
                    db.session.add(find_id)
            try:
                db.session.commit()
                flash({'type':'ok','message':u'更新成功'})
            except:
                flash({'type':'error','message':u'更新失败'})
    return jsonify({'code':200})


#查看该权限下的用户名以及删除功能
@auth.route('/permission_users', methods=['GET','POST'])
@login_required
@admin_required
@csrf.exempt
def permission_users():

    def return_users(id):
        find_users = Permission_Model.query.filter_by(id = id).first()
        return find_users


    if request.method == 'POST':
        id = request.form.get('id')
        users = [ user.username for user in return_users(id).users ]
        return jsonify({'code':200, 'users':'  |  '.join(users)})
    elif request.method == 'GET':
        id = request.args.get('id')
        if return_users(id).users:
            return jsonify({'code':400, 'message':u'关联用户不为空'})
        else:
            try:
                delete_db(return_users(id))
                flash({'type':'ok', 'message':u'删除完成'})
                return jsonify({'code':200})
            except:
                return jsonify({'code':400, 'message':u'删除异常'})