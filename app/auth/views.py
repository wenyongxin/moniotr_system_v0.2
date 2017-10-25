#!/usr/bin/env python
#ecoding:utf-8

from flask import render_template, redirect, request, url_for, flash, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db, csrf
from ..models import User, Role, Sections, Icon, Permission_Model
from ..scripts.xtcaptcha import Captcha
from io import BytesIO
from ..scripts.tools import save_db,delete_db,save_many_to_many,get_user_infos,get_user_email_or_telphone, \
    urldecode,flush_token, save_memcache_value, get_memcached_value
from ..decorators import admin_required
from urllib import unquote
from werkzeug.utils import secure_filename
import json, sys, os
sys.path.append('../..')
import config





#测试页面
@auth.route('/manager_test')
@login_required
def manager_test():
    # #1 先筛选出当前权限id的对应编号
    # res = Permission_Model.query.filter_by(id = current_user.permission_id).first()
    # #2 找出版块名称
    # sectionss,sections_list = [],[]
    # for f_sections in res.section:
    #     if f_sections.head and f_sections.membership == None:
    #         sectionss.append(f_sections)
    # #3 通过匹配id与membership是否相同。如果相同则对方称一个列表
    # for f_urls in sectionss:
    #     local_urls = []
    #     for f_sections in res.section:
    #         if f_urls.id == f_sections.membership:
    #             local_urls.append(f_sections)
    #     print f_urls
    #     print local_urls
    #     sections_list.append({'section':f_urls, 'urls':local_urls})

    print current_user.sesctions(current_user.permission_id)

    http_data = {
        'name':u'测试页面',
    }
    return render_template('manager/manager_test.html', **http_data)



# @auth.route('/register', methods=['GET', 'POST'])
# def register():
#     pass
#     # form = RegistrationForm()
#     # if form.validate_on_submit():
#     #     user = User(email=form.email.data,
#     #                 username=form.username.data,
#     #                 password=form.password.data)
#     #     db.session.add(user)
#     #     db.session.commit()
#     #     # token = user.generate_confirmation_token()
#     #     # send_email(user.email, 'Confirm Your Account',
#     #     #            'auth/email/confirm', user=user, token=token)
#     #     flash('A confirmation email has been sent to you by email.')
#     #     return redirect(url_for('auth.login'))
#     # return render_template('auth/register.html', form=form)
#
#
# @auth.route('/confirm/<token>')
# @login_required
# def confirm(token):
#     pass
#     # if current_user.confirmed:
#     #     return redirect(url_for('main.index'))
#     # if current_user.confirm(token):
#     #     flash('You have confirmed your account. Thanks!')
#     # else:
#     #     flash('The confirmation link is invalid or has expired.')
#     # return redirect(url_for('main.index'))
#
#
# @auth.route('/confirm')
# @login_required
# def resend_confirmation():
#     pass
#     # # token = current_user.generate_confirmation_token()
#     # # send_email(current_user.email, 'Confirm Your Account',
#     # #            'auth/email/confirm', user=current_user, token=token)
#     # flash('A new confirmation email has been sent to you by email.')
#     # return redirect(url_for('main.index'))
#
#
# # @auth.route('/change-password', methods=['GET', 'POST'])
# # @login_required
# # def change_password():
# #     pass
#     # form = ChangePasswordForm()
#     # if form.validate_on_submit():
#     #     if current_user.verify_password(form.old_password.data):
#     #         current_user.password = form.password.data
#     #         db.session.add(current_user)
#     #         flash('Your password has been updated.')
#     #         return redirect(url_for('main.index'))
#     #     else:
#     #         flash('Invalid password.')
#     # return render_template("auth/change_password.html", form=form)
#
#
# @auth.route('/reset', methods=['GET', 'POST'])
# def password_reset_request():
#     pass
#     # if not current_user.is_anonymous:
#     #     return redirect(url_for('main.index'))
#     # form = PasswordResetRequestForm()
#     # if form.validate_on_submit():
#     #     user = User.query.filter_by(email=form.email.data).first()
#     #     # if user:
#     #     #     token = user.generate_reset_token()
#     #     #     send_email(user.email, 'Reset Your Password',
#     #     #                'auth/email/reset_password',
#     #     #                user=user, token=token,
#     #     #                next=request.args.get('next'))
#     #     flash('An email with instructions to reset your password has been '
#     #           'sent to you.')
#     #     return redirect(url_for('auth.login'))
#     # return render_template('auth/reset_password.html', form=form)
#
#
# @auth.route('/reset/<token>', methods=['GET', 'POST'])
# def password_reset(token):
#     pass
#     # if not current_user.is_anonymous:
#     #     return redirect(url_for('main.index'))
#     # form = PasswordResetForm()
#     # if form.validate_on_submit():
#     #     user = User.query.filter_by(email=form.email.data).first()
#     #     if user is None:
#     #         return redirect(url_for('main.index'))
#     #     if user.reset_password(token, form.password.data):
#     #         flash('Your password has been updated.')
#     #         return redirect(url_for('auth.login'))
#     #     else:
#     #         return redirect(url_for('main.index'))
#     # return render_template('auth/reset_password.html', form=form)
#
#
# @auth.route('/change-email', methods=['GET', 'POST'])
# @login_required
# def change_email_request():
#     pass
#     # form = ChangeEmailForm()
#     # if form.validate_on_submit():
#     #     if current_user.verify_password(form.password.data):
#     #         new_email = form.email.data
#     #         token = current_user.generate_email_change_token(new_email)
#     #         # send_email(new_email, 'Confirm your email address',
#     #         #            'auth/email/change_email',
#     #         #            user=current_user, token=token)
#     #         flash('An email with instructions to confirm your new email '
#     #               'address has been sent to you.')
#     #         return redirect(url_for('main.index'))
#     #     else:
#     #         flash('Invalid email or password.')
#     # return render_template("auth/change_email.html", form=form)
#
#
# @auth.route('/change-email/<token>')
# @login_required
# def change_email(token):
#     pass
#     # if current_user.change_email(token):
#     #     flash('Your email address has been updated.')
#     # else:
#     #     flash('Invalid request.')
#     # return redirect(url_for('main.index'))
