#!/usr/bin/env python
#ecoding:utf-8
#自定义过滤器


import json, flask, config, re
from app.scripts.redis_manage import Efun_Redis
from app.scripts.tools import get_memcached_value, save_memcache_value




def custom_filters(app):

    #自定义前端过滤器。通过传参id自定显示名称
    def to_name(id):
        url = flask.request.path.split('/')[-1]
        return json.loads(Efun_Redis.redis_get(url))[id]
    app.add_template_filter(to_name, 'to_name')

    #自定义过滤器，前端页面的字符串转换成列表
    def to_list(str):
        return str.split(',')
    app.add_template_filter(to_list, 'to_list')

    #游戏负责人对应表模块 game_ascription
    #用于返回运营中心名称
    def return_name(id):
        return config.efun_centers.get(id, u'未找到')
    app.add_template_filter(return_name, 'return_name')

    #通过返回布尔值的是或否
    def return_bol(bol):
        if bol:return u'是'
        else:return u'否'
    app.add_template_filter(return_bol, 'return_bol')

    #返回游戏名称
    def return_game_name(id):
        get_info = get_memcached_value('center_hostgroup_name')
        all_dicts = {}
        for a in get_info.values():
            all_dicts.update(a)
        try:
            return all_dicts[id]
        except:
            return u'名称失效'
    app.add_template_filter(return_game_name, 'return_game_name')


    #用于做判断是否审批通过，如果审批不通过则返回False，审批通过返回True
    def is_approve(value):
        pass


    #根据主机组返回该游戏的第一第二负责人
    def return_ascription(groups):
        try:
            for i in groups:
                ascription = get_memcached_value("ascription_data")
                if int(i['groupid']) in ascription.keys():
                    if ascription[int(i['groupid'])]:
                        return ascription[int(i['groupid'])]
        except:
            return u'未找到'

    app.add_template_filter(return_ascription, 'return_ascription')


    #根据传回的时间戳判断该故障时长
    def problem_long_time(stamp):
        from datetime import datetime
        from scripts.time_manage import strftime_to_datetime

        time = strftime_to_datetime(stamp)

        if type(time) == datetime:
            now = datetime.now()
            timestamp = (now - time).total_seconds()
            if timestamp < 60:
                return u'刚刚'
            elif timestamp > 60 and timestamp < 60*60:
                minutes = timestamp / 60
                return u'%s分钟前' % int(minutes)
            elif timestamp > 60*60 and timestamp < 60*60*24:
                hours = timestamp / (60*60)
                return u'%s小时前' % int(hours)
            elif timestamp > 60*60*24 and timestamp < 60*60*24*30:
                days = timestamp / (60*60*24)
                return u'%s天前' % int(days)
            elif timestamp > 60*60*24*30 and timestamp < 60*60*24*30*12:
                month = timestamp / (60*60*24*30)
                return u'%s月前' % int(month)
            else:
                year = timestamp / (60*60*24*30*12)
                return u'%.2f 年前' % year
        else:
            return u'无法计算'

    app.add_template_filter(problem_long_time, 'problem_long_time')


    #判断您是否关闭报警
    def is_close_message(triggerid):
        try:
            is_close = get_memcached_value(triggerid)
            if is_close:
                return is_close
            else:
                return False
        except:
            return False

    app.add_template_filter(is_close_message, 'is_close_message')

    #itemid的id列表
    def itemids_to_list(data):
        return [ int(d['itemid']) for d in data ]
    app.add_template_filter(itemids_to_list, 'itemids_to_list')



    #通过itemid方式返回对应的名称
    def return_itemid_name(itemid, ip):
        from app.scripts.zabbix_manage import manage_zabbix
        zabbix = manage_zabbix()

        key = 'itemid_name_%s' %itemid
        if not get_memcached_value(key):
            name = zabbix.change_all_macro_name(itemid, ip)
            save_memcache_value(key, name, 60*60)
        else:
            name = get_memcached_value(key)

        return name
    app.add_template_filter(return_itemid_name, 'return_itemid_name')

    #通过graphid返回其对应的名字
    def return_graphid_name(graphid):

        key = 'graphid_%s' %graphid
        name = get_memcached_value(key)
        return name

    app.add_template_filter(return_graphid_name, 'return_graphid_name')

    #判断当前的item的历史记录是否为log类型
    def is_string(something):
        try:
            float(something)
            return False
        except:
            return True

    app.add_template_filter(is_string, 'is_string')

    #将时间戳传换成年月十分
    def web_strftime_to_date(strftime):

        from app.scripts.time_manage import strftime_to_date
        return strftime_to_date(int(strftime))

    app.add_template_filter(web_strftime_to_date, 'web_strftime_to_date')






