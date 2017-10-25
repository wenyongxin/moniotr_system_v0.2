#!/usr/bin/env python
#ecoding:utf-8


from app.monitor import monitor
from flask import render_template, request, jsonify, url_for, redirect, Response
from flask_login import login_required, current_user
from ..decorators import user_required, zabbix_login_required
from ..scripts.zabbix import zabbix_API
from ..scripts.zabbix_manage import manage_zabbix
from ..scripts.tools import save_memcache_value,get_memcached_value
from .models import Game_Ascritption
from ..scripts.xtcaptcha import Captcha
from app import csrf
import sys
from PIL import Image
from io import BytesIO
sys.path.append('../..')
import config

zabbix = manage_zabbix()

#用于做zabbix页面刷新工作
#此处主要先验证当前输入的zabbix账号是否正确。
#如果正确则存储在memcached中。
#默认保存周期为7天。7天以后会自动的删除，届时需要重新的登录
#通过装饰器，做了zabbix的登录验证，如果没有该用户的登录信息。则跳转到登录
#验证通过后保存在缓存中，下次登录装饰器会检查是否能找到，如果找不到则需要重新的登录
@monitor.route('/monitor/zabbix_login', methods=['GET','POST'])
@login_required
@csrf.exempt
def zabbix_login():
    html_data = {
        'name':u'zabbix绑定'
    }
    if request.is_xhr and request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        zabbix = zabbix_API(
                action='auth',
                zabbix_user=user,
                zabbix_password=password,
                zabbix_server=config.zabbix_server)
        auth = zabbix.login()
        sid = Captcha.gene_text(16).lower()
        if auth:
            #默认保存7天
            save_memcache_value(current_user.zabbix_user_key(), auth, 60*60*24*7)
            save_memcache_value(auth, {'user':user, 'password':password, 'sid':sid}, 60*60*24*7)

            return jsonify({'code':200, 'href': url_for('monitor.zabbix_scan')})
        else:
            return jsonify({'code':400, 'message':u'验证错误'})
    return render_template('monitor/zabbix_login.html', **html_data)


#显示zabbix的页面报警信息
@monitor.route('/monitor/scan', methods=['GET','POST'])
@login_required
@user_required
@zabbix_login_required
def zabbix_scan():

    #往memcached存放游戏负责人临时信息
    if not get_memcached_value("ascription_data"):
        ascription_data = { int(name.game_name):'%s %s' %(name.game_one, name.game_two) for name in Game_Ascritption.query.all() }
        save_memcache_value('ascription_data', ascription_data, 60*60*1)

    #从memcached中读取当前用户的zabbix验证秘钥 默认有效期为7天
    auth = get_memcached_value(current_user.zabbix_user_key())

    html_data = {
        'name':u'监控查看',
        'auth':auth
    }
    return render_template('monitor/zabbix_scan.html', **html_data)

#用于调用zabbix异常的信息

@monitor.route('/monitor/zabbix.json', methods=['POST'])
@login_required
@zabbix_login_required
@csrf.exempt
def zabbix_police_infos():

    problem_triggerids,show_infos = [],[]

    if request.is_xhr and request.method == 'POST':
        auth,fun = request.form['auth'],request.form['fun']
        name_dict = {u'维护':0, u'故障':1}

        try:
            all_hostids = get_memcached_value('all_hostids')

            if not all_hostids:
                hostids_dict = { h['hostid']:[ g['groupid'] for g in h['groups']] for h in zabbix.get_hostid(auth=auth) }
                save_memcache_value('all_hostids', hostids_dict, 60*30)

            if fun.encode('utf8') == '维护':
                triggers = zabbix.get_hostids_trigger(all_hostids.keys(), auth=auth, maintenance=True)
            elif fun.encode('utf8') == '故障':
                triggers = zabbix.get_hostids_trigger(all_hostids.keys(), auth=auth, maintenance=False)

            if triggers:
                for i in triggers:
                    if int(i['items'][0]['status']) == 0:
                        problem_triggerids.append(i['triggerid'])
                        show_infos.append(i)

            #将报警的信息保存在memcached中。id则根据zabbix的usergroup来区分
            # try:
            #     username = get_memcached_value(auth)
            #     filter = {"alias":username['user']}
            #     userid = zabbix.get_ures_names(filter)[0]['userid']
            #     key = 'zabbix_problem_%s_%s' %(zabbix.userid_get_groupid(userid)[0]['usrgrpid'], name_dict[fun])
            #     if not get_memcached_value(key):
            #         save_memcache_value(key, show_infos, 60)
            #     else:
            #         show_infos = get_memcached_value(key)
            # except BaseException,e:
            #     pass

            #通过多线程方式快速获取到已经关闭报警的报警项目
            if problem_triggerids:
                zabbix.multi_get_ack(problem_triggerids, auth=auth)
        except BaseException,e:
            pass
        return render_template('monitor/monitor_scan_table.html', show_infos=show_infos)
    else:
        return redirect(url_for('monitor.zabbix_login'))


#图片已数据流的方式返回
@monitor.route('/monitor/graph.png')
@login_required
@zabbix_login_required
@csrf.exempt
def zabbix_police_graph():
    #get方式获取itemid
    if request.method == 'GET':
        itemid, graphid = request.args.get('itemid'), request.args.get('graphid')

        auth = get_memcached_value(current_user.zabbix_user_key())
        if itemid:
            data = zabbix.return_item_graph(auth, itemid)

        elif graphid:
            data = zabbix.return_graphid_graph(auth, graphid)

        out = BytesIO()  #获取管道
        out.write(data)
        out.seek(0) #移动指针到第0个位置，如果不移动下面无法正常读取到该图片
        response = Response(out.read(),content_type='image/png')
        return response


#点击方式创建一个zabbix页面的url地址
@monitor.route('/monitor/to_zabbix')
@login_required
@zabbix_login_required
def to_zabbix():
    if request.is_xhr and request.method == 'GET':
        itemid,graphid = request.args.get('itemid'), request.args.get('graphid')
        boole = request.args.get('boole')

        if itemid:
            if boole == 'True':
                to_zabbix_url = '%s/history.php?action=showgraph&itemids[]=%s' %(config.zabbix_server, itemid)
            elif boole == 'False':
                to_zabbix_url = '%s/history.php?action=showvalues&itemids[]=%s' %(config.zabbix_server, itemid)

        elif graphid:
            hostid = request.args.get('hostid')
            to_zabbix_url = '%s/charts.php?hostid=%s&graphid=%s' %(config.zabbix_server, hostid, graphid)

        return to_zabbix_url



#############################################################
#用于爬去zabbix信息在前端显示
#############################################################

#zabbix grouph图web页面
@monitor.route('/monitor/showgraph')
@login_required
@zabbix_login_required
@csrf.exempt
def show_item_graphs():
    if request.is_xhr and request.method == 'GET':

        html_data = {
            'itemids': request.args.get('itemids').split(','),
            'ip': request.args.get('ip'),
            'boole':True
        }

        return render_template('/temp/showgraph.html', **html_data)

#通过传入的hostid地址,返回其下方有多少个graph信息
@monitor.route('/monitor/selectgraph')
@login_required
@zabbix_login_required
@csrf.exempt
def show_graph_graphs():

    if request.is_xhr and request.method == 'GET':

        hostid = request.args.get('hostid')
        graphids = []

        try:
            for i in zabbix.hostid_to_graphids(hostid):
                graphids.append(i['graphid'])
                key = 'graphid_%s' %i['graphid']
                save_memcache_value(key, i['name'], 60*60)
        except:pass

        html_data = {
            'graphids':graphids,
            'boole':True
        }

        return render_template('/temp/showgraph.html', **html_data)


#通过传入itemid返回一小时的历史记录
@monitor.route('/monitor/showvalue')
@login_required
@zabbix_login_required
@csrf.exempt
def show_item_value():

    if request.is_xhr and request.method == 'GET':
        itemid = request.args.get('itemid')
        data = []
        try:
            for i in zabbix.itemid_to_history(itemid):
                if i['value']:
                    data.insert(0,i)
        except:pass

        html_data = {
            'data':data,
            'boole':False
        }

        return render_template('/temp/showgraph.html', **html_data)


