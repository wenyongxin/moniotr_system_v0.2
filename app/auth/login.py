#!/usr/bin/env python
#ecoding:utf-8

'''
功能：
登录管理视图函数
用户管理视图函数
用户头像上传
用户资料修改
用户密码修改
用户删除
'''

from flask import render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import csrf
from ..models import User, Role, Permission_Model
from ..scripts.xtcaptcha import Captcha
from ..scripts.tools import save_db,delete_db,get_user_infos,get_user_email_or_telphone, \
    urldecode,flush_token, save_memcache_value, get_memcached_value
from ..decorators import admin_required
from urllib import unquote
from werkzeug.utils import secure_filename
import sys, os
sys.path.append('../..')
import config


#登录视图函数
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.is_xhr:
        send_mail = request.form.get('email')
        if '@efun.com' in send_mail:
            return jsonify({'code':500, 'des':u'不要加邮箱后缀'})

        full_email = '%s@efun.com' %send_mail
        user = User.query.filter_by(email = full_email).first()

        #判断用户是否被禁用，如果禁用直接返回，没有禁用则继续操作
        if not send_mail:
            return jsonify({'code':500, 'des':u'用户名不能为空'})
        elif not user:
            return jsonify({'code':500, 'des':u'用户不存在'})
        elif user.status:
            return jsonify({'code':600, 'des':u'用户已经禁用，请联系管理员！', 'href':'/'})

        password = request.form.get('password')
        if user is not None and user.verify_password(password):

            #如果从缓存中没有找到该浏览器在错误的情况下产生的缓存信息以及没有值得情况下跳过验证码校验
            captcha = request.form.get('captcha')

            if captcha:
                if not Captcha.check_captcha(captcha.lower()):
                    return jsonify({'code':500, 'des':u'验证码错误或过期请点击更新'})
            else:
                return jsonify({'code':500, 'des':u'请输入验证码'})
            #判断是否为初始密码，如果是则跳转页面提醒修改密码，并有复杂度的要求


            #将密码记录到本地
            if request.form.get('remember_me') == u'false':
                login_user(user, False)
            else:
                login_user(user, True)
            if password == config.default_login_passwd:
                return jsonify({'code':600, 'des':u'首次登陆必须修改密码！', 'href':'/auth/change_password'})
            #获取页面跳转的信息，如果有get到页面跳转的信息则返回页面跳转界面如果没有则index为主页
            next_page = request.form.get('new_href', '')
            if not next_page:
                next_page = url_for('main.index')
            else:
                next_page = unquote(next_page).split('?next=')[1]
            return jsonify({'code':200, 'des':u'验证成功', 'href':next_page})

        else:
            return jsonify({'code':400, 'des':u'用户名或密码错误'})
    return render_template('manager/login.html')




#退出登录函数，修改后ok
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


#用于用户管理，能够实现增、删、修改密码、权限、头像等工作
@auth.route('/manager_users', methods=['GET','POST'])
@login_required
@admin_required
@csrf.exempt
def manager_users():
    if request.is_xhr:
        username = request.form.get('username')
        try:
            open_id = get_user_infos(username)
            email = get_user_email_or_telphone(open_id, 'email')
            #通过邮箱判断该用户是否存在
            find_email = User.query.filter_by(email = email).first()
            if find_email:
                return jsonify({'code':400, 'message':u'%s 已经存在，不可重复添加' % username})
            telphone = get_user_email_or_telphone(open_id, 'telphone')
            department = int(request.form.get('department'))
            permission = int(request.form.get('permission'))
        except:
            return jsonify({'code':400, 'message':u'%s 未找到，请检查输入名字是否正确' % username})

        create_user = User(
                email = email,
                username = username,
                password = config.default_login_passwd,
                department = config.department[department],
                telphone = telphone
            )
        find_permission = Permission_Model.query.filter_by(id=permission).first()
        find_permission.users.append(create_user)
        try:
            save_db(find_permission)
        except:
            flash({'type':'error','message':u'%s 用户创建创建异常' %username})
            return jsonify({'code':400, 'message':u'%s创建失败' %username})
        if not email or not telphone:
            flash({'type':'error','message':u'创建异常'})
            return jsonify({'code':400, 'message':u'%s用户信息提取失败，请手动加入！' %username})
        else:
            flash({'type':'ok','message':u'创建成功'})
            return jsonify({'code':200})

    html_data = {
        'name':u"用户管理",
        'db_rose': Role.query.all(),
        'department':config.department,
        'permission':{ per.id: per.name for per in Permission_Model.query.all()}
    }

    return render_template('manager/manager_users.html', **html_data)


#通过get方式获取用户的id，返回相关信息，该功能用于在用户管理模块中可修改用户信息
@auth.route('/edit_user')
@login_required
@admin_required
def edit_user():
    if request.is_xhr:
        id = request.args.get('id')
        html_data = {
            'user': User.query.filter_by(id=id).first(),
            'department':config.department,
            'roles': { role.id: role.name for role in Role.query.all()},
            'permission':{ per.id: per.name for per in Permission_Model.query.all()},
            'default_password':config.default_login_passwd,
            'status_list':config.status_list
        }
        return render_template('manager/alert_user.html', **html_data)

#用户信息更新
@auth.route('/user_update', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def user_update():

    if request.is_xhr:
        datas = urldecode(request.get_data())
        try:
            find_user = User.query.filter_by(id=datas['id']).first()
            if not find_user.email:
                find_user.email = datas['email'].lower()
            find_user.department = config.department[int(datas['department'])]
            find_user.telphone = datas['telphone']
            if int(datas['user_status']) == 0:
                find_user.status = False
            else:
                find_user.status = True
            #修改密码
            if datas['password'] != config.default_login_passwd:
                find_user.password = datas['password']

            if int(datas['roles']) == 1:
                find_rose = Role.query.filter_by(name='Administrator').first()
                find_permission = Permission_Model.query.filter_by(id=1).first()
            else:
                if int(datas['permission']) == 1:
                    return jsonify({'code':400, 'message':u'权限不可再选择 超级管理'})
                else:
                    find_rose = Role.query.filter_by(id = datas['roles']).first()
                    find_permission = Permission_Model.query.filter_by(id=datas['permission']).first()

            find_rose.users.append(find_user)
            find_permission.users.append(find_user)
            save_db(find_user)

            flash({'type':'ok', 'message':u'更新成功!'})
            return jsonify({'code':200})
        except:
            return jsonify({'code':400, 'message':''})


#用户更新头像
@auth.route('/update_image', methods=['POST','GET'])
@login_required
@csrf.exempt
def update_image():
    if request.method == "POST":
        file = request.files['file']
        userid = request.form.get('userid')
        filepath = r'%s/app/static/users/images/' % config.basedir
        filename = '%s.%s' %(flush_token(5),secure_filename(file.filename).split('.')[-1])
        #保存到本地
        file.save(os.path.join(filepath, filename))
        #保存到本地数据库中
        find_user = User.query.filter_by(id=userid).first()
        #删除以前的头像图片
        try:
            if find_user.avatar != u"default.jpg":
                old_image = r'%s/app/static/users/images/%s' % (config.basedir,find_user.avatar)
                os.remove(old_image)
        except:pass
        find_user.avatar = filename
        save_db(find_user)
        #将文件名存储到memcache的缓存中
        save_memcache_value(find_user.email, filename)
        return jsonify({'code':200, 'message':u'上传成功'})
    else:
        userid = request.args.get('id')
        find_user = User.query.filter_by(id=userid).first()
        role = find_user.role.name
        filename = get_memcached_value(find_user.email)
        image = r'../static/users/images/%s' %filename
        return jsonify({'code':200, 'image':image, 'role':role})


#用户删除账号
@auth.route('/user_delete', methods=['GET'])
@login_required
@admin_required
@csrf.exempt
def user_delete():
    if request.is_xhr:
        id = request.args.get('id')
        find_user = User.query.filter_by(id=id).first()
        try:
            if find_user.avatar != u"default.jpg":
                old_image = r'%s/app/static/users/images/%s' % (config.basedir,find_user.avatar)
                os.remove(old_image)
            delete_db(find_user)
            flash({'type':'ok', 'message':u'用户删除完成'})
        except:
            flash({'type':'error', 'message':u'用户删除失败'})
        return jsonify({'code':200})


#修改密码
@auth.route('/change_password', methods=['GET','POST'])
@login_required
@csrf.exempt
def change_password():
    name = u'修改密码'
    if request.is_xhr:
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        if current_user.verify_password(old_password):
            current_user.password = new_password
            save_db(current_user)
            flash({'type':'ok', 'message':u'密码修改完成'})
            return jsonify({'code':200})
        else:
            flash({'type':'error', 'message':u'密码错误'})
            return jsonify({'code':400})
    return render_template('/manager/change_password.html' ,name=name)
