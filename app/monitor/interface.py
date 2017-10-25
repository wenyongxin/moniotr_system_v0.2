#ecoding:utf-8
from flask import request
from flask_login import current_user
from app.monitor import monitor
from app import db
from app.models import  Monitor_host, Login_pwd, Login_ssh
import json
import sys, time
from app.scripts.tools import urldecode, return_id, select_and_create, save_db, return_ips, save_memcached_list
from app.scripts.socket_client import Run_Socket_Client
sys.path.append('../..')
import config


conn_memcache = config.conn_memcached()




#将接收的json数据做转换
def insert_db(data):
    db.session.add(data)
    try:
        db.session.commit()
        return True
    except:
        return False

#读取日志文件
def read_log(filename):
    with open(filename, 'r') as f:
        return return_ips(f.read())


#通过接收post信息，将该信息存储到数据库中
@monitor.route('/monitor/message_interface', methods=['POST','GET'])
def message_interface():
    try:datas =  eval(request.get_data())
    except:datas = urldecode(request.get_data())
	
    if Monitor_host.query.filter_by(token=datas['token']).all():
        #当前接收的主机token是否与Monitor_host中的主机token是否相同。如果不相同则跳过写入数据库。拒绝从该ip的连接
        if datas.has_key('time'):
            now_time = datas['time']
        else:
            now_time = time.strftime('%H:%M:%S',time.localtime(time.time()))


        if int(datas['plan']) > 0 :
            #用于在memcached中存储1%--100%的进度
            message_data = {'host':datas['host'], 'plan':datas['plan'], 'message':datas['message'], 'time':now_time, 'code':datas['code'], 'token':datas['token']}
            save_memcached_list(config.memcached_key_name(datas['userid'])[1], message_data)
            conn_memcache.set_multi({datas['host']: datas['plan']}, 3600, key_prefix="plan_")
        else:
            #用于在memcached中存储-1%的检测信息
            conn_memcache.set_multi({datas['host']:datas['message']}, 3600, key_prefix='check_')
        return u'%s %s\n' %(datas['host'], datas['message'])
    else:
        return 'error'



#monitor_history数据库中读取信息到前端口页面
@monitor.route('/monitor/message_info', methods=['GET','POST'])
def message_info():
    #局部变量
    return_json, check_info, dont_conn= {},{},[]
    plan_text, monitor_check = "",""
    html_text, userid = '<table class=\"table\">',current_user.id

    if request.method == "POST":
        #通过memcached获取进度相关的数据
        recv_datas = conn_memcache.get(config.memcached_key_name(userid)[0])
        try:
            ips = recv_datas['ips'].split(',')
            plan_item = conn_memcache.get_multi(ips, key_prefix='plan_')
            #用于在前端页面显示进度条
            for ip,plan in plan_item.items():
                if plan:
                    plan_text += '<span class=\"c_ip\">%s</span><div class=\"progress\"><div class=\"progress-bar progress-bar-striped active\" role=\"progressbar\" aria-valuenow=\"20\" aria-valuemin=\"0\" aria-valuemax=\"100\" style=\"width: %s%%;\"></div></div>' %(ip, plan)
		
            #用于在前端页面显示实时状态
            for line in conn_memcache.get(config.memcached_key_name(userid)[1]):
                check_info[line['host']] = line['token']
                html_text += "<tr><td style=\"color:green\">%s</td><td style=\"color:red\">%s</td><td>%s</td><td>%s%%</td>" %(line['host'], line['time'], line['message'], line['plan'])
            html_text += "</table>"

            #用于判断当前状态下是否需要做检测
            find_cache_check =  conn_memcache.get_multi(plan_item.keys(),key_prefix='check_')
            rar_list = list(set(plan_item.values()))
            if len(rar_list) == 1 and '100' in rar_list:
                if not find_cache_check:
                    check_data = {'conn_pwd':'0new0rd','proxy_ip':recv_datas['proxy'], 'host':check_info,
							'monitor_host':config.monitor_url, "userid":userid, "action":"check"}
                    Run_Socket_Client(check_data, config.monitor_check_host)

            if find_cache_check:
                monitor_check = "<table class=\"table\">"
                for ip,message in find_cache_check.items():
                    monitor_check += "<tr><td>%s</td>" %ip
                    for mess in message.split('+'):
                        if u'异常' in mess:
                            monitor_check += "<td style=\"color:red;\">%s</td>" %mess
                        else:
                            monitor_check += "<td style=\"color:green;\">%s</td>" %mess
                    monitor_check += "</tr>"
                monitor_check += "</table>"

            #判断连接异常IP地址的
            find_ok_ips = conn_memcache.get(config.memcached_key_name(userid)[2])
            if find_ok_ips:
                ok_ips = []
                for ok_dict in find_ok_ips:
                    ok_ips.append(ok_dict.keys()[0])
                    #将对应的用户名密码信息存储到数据库中
                    find_db = Monitor_host.query.filter_by(ipaddr = ok_dict.keys()[0], user=current_user.username).first()
                    #用于判断输入的密码或端口号是否存在。如果不存在则添加到数据库中。这里先预留了一个判断真假的功能，如果为真则不刷新redis为假则刷新redi
                    new_pwd, new_port = ok_dict.values()[0][0], int(ok_dict.values()[0][1])
                    select_and_create(Login_pwd, new_pwd, 'pwd')
                    select_and_create(Login_ssh, new_port, 'port')
                    find_db.login_pwd_id = return_id(Login_pwd, 'pwd', 'r_id', new_pwd)
                    find_db.login_ssh_id = int(return_id(Login_ssh, 'port', 'r_id', new_port))
                    save_db(find_db)
                if len(ok_ips) != len(ips):
                    [ ips.remove(o_ip) for o_ip in ok_ips ]
                    dont_conn = ips

                #清空指定ip密码端口临时缓存
                conn_memcache.delete(config.memcached_key_name(userid)[2])
        except StandardError,e:
            pass


        return_json['plan'],return_json['message'],return_json['except'],return_json['check'] = plan_text,html_text,','.join(dont_conn),monitor_check


        return json.dumps(return_json)
    else:
        return json.dumps({'code':'404'})
