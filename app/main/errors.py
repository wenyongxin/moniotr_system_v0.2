#!/usr/bin/env python
#ecoding:utf-8


from flask import render_template
from . import main


@main.app_errorhandler(403)
def forbidden(e):
    html_datas = {
        'name':403,
        'message':u'没有权限访问此网页，请联系管理员。。。'
    }
    return render_template('error.html', **html_datas), 403


@main.app_errorhandler(404)
def page_not_found(e):
    html_datas = {
        'name':404,
        'message':u'页面开发中。请耐心等待。。。'
    }
    return render_template('error.html', **html_datas), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    html_datas = {
        'name':500,
        'message':u'页面去火星了，请耐心等它回来。。。'
    }
    return render_template('error.html', **html_datas), 500
