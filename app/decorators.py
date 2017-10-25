#!/usr/bin/env python
#ecoding:utf-8

from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user
from .models import Permission
from app.scripts.tools import get_memcached_value


#1 先判断用户是否为管理员。
#2 如果是管理员直接返回不做检测
#3 如果非管理员则检测路径是否具有访问权限
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_admin() and current_user.can(permission):
                return f(*args, **kwargs)
            else:
                if not current_user.show_sections():
                    abort(403)
                else:
                    return f(*args, **kwargs)
        return decorated_function
    return decorator

#限定普通用户的
def user_required(f):
    return permission_required(Permission.user)(f)

#限定超级管理员的
def admin_required(f):
    return permission_required(Permission.administrator)(f)



#判断当前用户有没有绑定zabbix用户，如果没有绑定则跳转页面
def zabbix_login_required(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        key = current_user.zabbix_user_key()
        if get_memcached_value(key):
            return f(*args,**kwargs)
        else:
            return redirect(url_for('monitor.zabbix_login'))
    return wrapper