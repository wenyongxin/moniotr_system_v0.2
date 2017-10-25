#!/usr/bin/env python
#ecoding:utf-8


#用途：
#用于做游戏归属查询


from app.monitor import monitor
from flask import render_template, request, jsonify, flash
from models import Game_Ascritption
from ..scripts.zabbix_manage import manage_zabbix
from flask_login import login_required, current_user
from app.scripts.tools import get_memcached_value, save_db, save_memcache_value, delete_db,dict_sorted, del_memcache_key
from app import csrf
from ..decorators import user_required
import sys
sys.path.append('../..')
import config


#全局变量
zabbix = manage_zabbix()


#全局
@monitor.route('/monitor/ascription', methods=['GET','POST'])
@login_required
@user_required
def ascription():

    #开启页面做一次游戏主机名称的缓存
    zabbix.find_hostgroup_names([ '%s_' %n[0:2] for n in config.efun_centers.values() ])
    # print current_user.is_admin()


    data_html = {
        'name':u'游戏负责人',
        'datas':Game_Ascritption.query.all()
    }

    return render_template('monitor/game_ascription.html', **data_html)

#弹框数据回调
@monitor.route('/monitor/ascription/<action>')
@login_required
def ascription_action(action):
    #更新op组名称
    zabbix.find_op_users()
    id = request.args.get('id')

    data_html = {
        'centers': config.efun_centers,
        'efun_op':get_memcached_value('op_users').keys(),
        'action':action
    }

    if action == 'create':
        data_html.update({'button_name':u'创建'})
        del_memcache_key('%s_id' %current_user.is_me())

    elif action == 'edit':
        data_html.update({'button_name':u'修改', 'edit_data':Game_Ascritption.query.get(id)})
        save_memcache_value('%s_id' %current_user.is_me(), id, 60*24)

    elif action == 'del':
        find_db = Game_Ascritption.query.get(id)
        try:
            delete_db(find_db)
            flash({'type':'ok','message':u'删除成功'})
        except:
            flash({'type':'error','message':u'删除错误'})
        return jsonify({'code':201})

    return render_template('monitor/game_ascription_alert.html', **data_html)


#游戏列表回调
@monitor.route('/monitor/hostgrou')
@login_required
def return_option():
    if request.is_xhr and request.method == 'GET':
        id = get_memcached_value('%s_id' %current_user.is_me())

        center_name = request.args.get('ceneter')
        games = dict_sorted(get_memcached_value('center_hostgroup_name')[center_name])

        try:
            check_groupid = Game_Ascritption.query.get(id).game_name
        except:
            check_groupid = False

        html = ""
        for line in games:
            if check_groupid:
                if int(line[0]) == int(check_groupid):
                    html += "<option selected=\"selected\" value=%s>%s</option>" %(line[0], line[1])
                else:
                    html += "<option value=%s>%s</option>" %(line[0], line[1])
            else:
                html += "<option value=%s>%s</option>" %(line[0], line[1])
        return html


#数据增删改
#审批只真对zabbix权限的审批。
#在添加完毕之后，会自动的做zabbix权限的更新。
#如果添加人员为管理员则直接更新
#如果添加人员为普通人员则需要通过审批更新
@monitor.route('/monitor/ascription/action.json', methods=['POST'])
@login_required
@csrf.exempt
def data_action():

    def is_true(check):
        if check == 'true':
            return True
        else:
            return False


    if request.is_xhr and request.method == 'POST':
        action = request.form['action']
        business = request.form['business']
        ganmes = request.form['ganmes']
        op_one = request.form['op_one']
        op_two = request.form['op_two']
        operate = request.form['operate']
        factory = request.form['factory']
        autonmoy = is_true(request.form['autonmoy'])
        online = is_true(request.form['online'])


        if action == 'create':
            games = Game_Ascritption(
                   center_name = business, game_name = ganmes, game_one = op_one, game_two= op_two,
                   game_factory = factory, game_autonomy = autonmoy, game_operate = operate, game_online = online)
            try:
                save_db(games)
                flash({'type':'ok','message':u'添加成功'})
            except BaseException,e:
                flash({'type':'error','message':u'添加失败'})
        elif action == 'edit':
            id = request.form['id']
            find_db = Game_Ascritption.query.get(id)
            find_db.center_name = business
            find_db.game_name = ganmes
            find_db.game_one = op_one
            find_db.game_two = op_two
            find_db.game_factory = factory
            find_db.game_autonomy = autonmoy
            find_db.game_operate = operate
            find_db.game_online = online
            try:
                save_db(find_db)
                flash({'type':'ok','message':u'更新成功'})
            except BaseException,e:
                flash({'type':'error','message':u'更新失败'})

        #更新成功一次也就更新一次memcached中的信息
        ascription_data = { int(name.game_name):'%s %s' %(name.game_one, name.game_two) for name in Game_Ascritption.query.all() }
        save_memcache_value('ascription_data', ascription_data, 60*60*1)

        return jsonify({'code':200})


