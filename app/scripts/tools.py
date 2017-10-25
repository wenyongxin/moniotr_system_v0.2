#!/usr/bin/bash
#ecoding:utf-8

##########################################
#
#用于存储个程序调用的调用的模块包
#
##########################################

import sys
sys.path.append('../..')
import config

#memcache 功能开始--------------------------------------------------------------------------
conn_memcache = config.conn_memcached()

#memcached 计算次数的
def memcache_incr(key, time=120):
    if not conn_memcache.get(key):
        conn_memcache.set(key, 0, time)
    conn_memcache.incr(key)
    return conn_memcache.get(key)

#memcached 累加字符串
def save_memcached_list(key, data):
    if str(conn_memcache.get(key)) == 'None':
        conn_memcache.set(key, [data], 3600)
    else:
        a = conn_memcache.get(key)
        a += [data]
        conn_memcache.replace(key, a)

#memcache 获指定key的值
def get_memcached_value(key):
    return conn_memcache.get(key)


#memcache 删除指定的key
def del_memcache_key(key):
    return conn_memcache.delete(key)

#memcache 存储字典
def save_memcache_value(key,value, time=2*60):
    return conn_memcache.set(key, value, time)



#memcache 功能结束--------------------------------------------------------------------------

#python 字典按照value排序
def dict_sorted(dicts):
    return sorted(dicts.items(), key=lambda item:item[1])



#python urllib.urlencode数据转换会字典
def urldecode(data):
    from urllib import unquote
    return { i.split("=")[0]:i.split("=")[1] for i in unquote(data).split('&')}



#随机生成token 5位数的字符串,用于post验证
def flush_token(num=5):
    import random,string
    return string.join(random.sample([chr(i) for i in range(97,122)], num)).replace(' ','')



#删除多条数据。以列表形式历遍
def delete_dbs(data):
    from .. import db
    [ db.session.delete(d) for d in data ]
    db.session.commit()

#将数数据库存储以列表形式传入，全部存储
def save_list_db(data):
    from .. import db
    db.session.add_all(data)
    db.session.commit()


#当个存储数据库
def save_db(data):
    from .. import db
    db.session.add(data)
    db.session.commit()

#删除单个数据库
def delete_db(data):
    from .. import db
    db.session.delete(data)
    db.session.commit()

#存储db多对多
def save_many_to_many(sourdb, appenddb, new_checked, action='append'):
    from .. import db
    if new_checked:
        for new_id in new_checked:
            find_section = sourdb.query.filter_by(id=new_id).first()
            if action == 'remove':
                find_section.permission.remove(appenddb)
            else:
                find_section.permission.append(appenddb)
    db.session.commit()

########################################################################################################################


#企业ＱＱ功能开始##########################################################################################
#获取企业QQ的用户列表信息
def get_openid():
        import urllib, urllib2, sys, json
        sys.path.append('../..')
        import config

        new_qyqq_info = {}
        data = config.company_qq_get_data
        url = config.company_qq.user_list_url
        response = urllib2.urlopen(url, urllib.urlencode(data))
        list_data = json.loads(response.read())
        for i in list_data['data']['items']:
            new_qyqq_info[i['realname']] = i['open_id']
        return new_qyqq_info


#获取用户的资料信息
def get_user_info(open_id):
    import urllib, urllib2, sys, json
    sys.path.append('../..')
    import config

    data = config.company_qq_get_data
    data.update({'open_ids':open_id})
    url = config.company_qq.user_info
    response = urllib2.urlopen(url, urllib.urlencode(data))
    res_data = json.loads(response.read())
    return res_data['data'][open_id]


#获取用户邮箱或手机信息
def get_user_email_or_telphone(open_id, type):
    import urllib, urllib2, sys, json
    sys.path.append('../..')
    import config

    data = config.company_qq_get_data
    data.update({'open_ids':open_id})
    if type == 'email':
        url = config.company_qq.user_email
    elif type == 'telphone':
        url = config.company_qq.user_telphone
    response = urllib2.urlopen(url, urllib.urlencode(data))
    res_data = json.loads(response.read())
    return res_data['data'][open_id]






#通过传递名称从缓存中查找。如果没找到则重新加载生成新的用户列表信息。如果在查找不到则返回None，找到返回相关信息
def get_user_infos(name):
    #第一次从memcached中获取数据
    get_user_list = get_memcached_value(config.save_user_list_dict)
    if not get_user_list:  #如果memcached为空则添加数据
        user_list = get_openid()
        save_memcache_value(config.save_user_list_dict, user_list, 0)
    elif not get_user_list[name]:#如果memcached有数据但是没有想要的则更新数据
        user_list = get_openid()
        save_memcache_value(config.save_user_list_dict, user_list, 0)
    else:
        return get_user_list[name]



#企业ＱＱ功能结束##########################################################################################



#通过输入的数据进行判断数据库中是否存在，如果不存在则添加
def select_and_create(dbname, select_str, db_field_name):
    from ..models import Login_pwd, Login_ssh
    if db_field_name == 'pwd':
        find_db = dbname.query.filter_by(pwd=select_str).first()
        if not find_db:
            try:
                data = dbname(pwd=select_str, prob=1)
                save_db(data)
                return True
            except:pass
        else:return False
    elif db_field_name == 'port':
        find_db = dbname.query.filter_by(port=select_str).first()
        if not find_db:
            try:
                data = dbname(port=select_str, prob=1)
                save_db(data)
                return True
            except:pass
        else:return False



#检测指定tcp端口是否可用
def check_tcp(host, port):
    import os
    check_tcp_file = r'%s/app/scripts/check_tcp' %config.basedir
    os.system('chmod 777 %s' %check_tcp_file)
    check_cmd = r'%s -H %s -p %s' %(check_tcp_file, host, port) #定义命令格式
    if 'OK' in os.popen(check_cmd).read():
        return True
    else:
        return False


#后台错误日志存放位置
def write_log(path, user, function):
    import time
    now_time = time.strftime('%Y-%m-%d %X', time.localtime())
    #触发日期|触发用户|触发事件
    log_lines = '%s | %s | %s\n' %(now_time, user, function)
    log_files = '%s/logs/%s-error.log' %(path, time.strftime('%Y-%m-%d', time.localtime()))
    with open(log_files, 'a') as f:
        f.write(log_lines)
        f.flush()


#通过传入名称查找其id·
def return_id(dbname, grammar, select, query_field=None):
    from ..models import Login_pwd, Proxy, System, Login_ssh
    if grammar == 'pwd':
        if select != "r_id":
            return [ a.pwd for a in dbname.query.all() ]
        else:
            return dbname.query.filter_by(pwd=query_field).first().id
    elif grammar == 'port':
        if select != "r_id":
            return [ int(a.port) for a in dbname.query.all() ]
        else:
            return dbname.query.filter_by(port=query_field).first().id
    elif grammar == 'proxy_ip':
        if select != "r_id":
            return [ (a.proxy_ip, a.proxy_name) for a in dbname.query.all() ]
        else:
            return dbname.query.filter_by(proxy_ip=query_field).first().id
    elif grammar == 'sort_name':
        if select != "r_id":
            return [ (a.sort_name, a.full_name) for a in dbname.query.all() ]
        else:
            return dbname.query.filter_by(sort_name=query_field).first().id


#通过系统名称参会登录用户名
def return_user(datas):
    if datas['install_system'] == 'w':
        return 'administrator'
    else:
        return 'root'



#views_monitor.py通过输入data信息，返回确切的值
def return_input_value(datas, key):
    values_dict = {'pwd':['login_pwd', 'login_pwd2'], 'port':['login_port', 'login_port2']}
    if datas[values_dict[key][1]]:
        return datas[values_dict[key][1]]
    else:
        return datas[values_dict[key][0]]



#将错误发送回到本机接口
def Send_Message(host, plan, message, code, token):
    import urllib2, urllib,sys
    sys.path.append('../..')
    import config

    data = {'host': host, 'plan': plan, 'message': message, 'code': code, 'token': token}
    url = '%s/monitor/message_interface' %config.monitor_url
    req = urllib2.Request(url)

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, urllib.urlencode(data))


#在当前目录中写入两个临时文件
def write_file(filename, font):
    file_path = r'/tmp/%s' %filename
    with open(file_path, 'a') as f:
        f.write(font)
        f.flush()


#匹配字符串中的IP地址
def return_ips(data):
    import re
    reip = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
    return reip.findall(data)


#生成0-5的随机数字，即是监控脚本执行sleep的时间
def random_num():
    import random
    return random.randint(0, 5)


#返回上下文全局变量
def return_context_g(name):
    from flask import g
    return getattr(g, name)