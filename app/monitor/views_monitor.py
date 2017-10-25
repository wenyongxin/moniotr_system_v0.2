#ecoding:utf-8
from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.monitor import monitor
from app.models import Login_pwd, Proxy, System, Login_ssh, Monitor_host
import sys, json, os
from app.scripts.socket_client import Run_Socket_Client
from app.scripts.tools import urldecode, flush_token, delete_dbs, save_list_db, return_id, return_user, return_input_value, check_tcp, write_log, return_ips, write_file
from app import csrf
from app.decorators import admin_required
#导入配置文件
sys.path.append('../..')
import config


reload(sys)
sys.setdefaultencoding( "utf-8" )



path = os.getcwd()
conn_memcache = config.conn_memcached()


#安装监控页面
@monitor.route('/monitor', methods=['POST','GET'])
@login_required
@admin_required
@csrf.exempt
def monitor_install():
    userid = current_user.id
    save_data = {'ips':"",'proxy':""}
	
    return_dicts = conn_memcache.get(config.memcached_key_name(userid)[0])
    if not return_dicts:
        return_dicts = save_data


    html_datas = {
		'name' : u'监控安装',
		'pwds' : return_id(Login_pwd, 'pwd', "list"),
		'sshs' : return_id(Login_ssh, 'port', "list"),
		'proxys' : return_id(Proxy, 'proxy_ip', "list"),
		'systems' : return_id(System, 'sort_name', "list"),
		'ips': json.dumps(return_dicts),
		'cwp': check_tcp(config.w_install_socket_server, config.w_install_socket_port),
	}

    if request.method == 'POST':
        # 前段返回样式
		# mode=false&login_ip=&login_port=22&login_pwd=0new0rd&conn_proxy=103.227.128.16&install_system=c
		#{'login_port': '22', 'install_system': 'c', 'login_pwd': '0new0rd', 'conn_proxy': '103.227.128.16', 'login_ip': '172.16.5.240+172.16.5.241', 'mode': 'false'}
		#传入 Install_Start 格式  ips, password, port, kwargs
		# kwargs = {'filename':'install-agent.V2.0.sh', 'system':'c', 'proxy':'103.227.128.16'}

		#自动匹配传回的字符串
		#{'login_port': '22', 'install_system': 'c', 'login_pwd': '0new0rd', 'conn_proxy': '103.227.128.16', 'login_ip': '172.16.5.240+172.16.5.241', 'mode': 'true'}


        datas =  urldecode(request.get_data())

        kwargs = {'filename':'install-agent.V2.0.sh', 'system':datas['install_system'], 'proxy':datas['conn_proxy'], 'user_id':int(current_user.id)}
        ips = return_ips(datas['login_ip'])
        insert_dbs = []

        #指定清空memcached中的信息
        for mem_name in config.memcached_key_name(userid):
            try:conn_memcache.delete(mem_name)
            except:pass
        #清空检测结果
        try:conn_memcache.delete_multi(ips, key_prefix='check_')
        except:pass
        #清空进度
        try:conn_memcache.delete_multi(ips, key_prefix='plan_')
        except:pass


        ssh_password = return_input_value(datas, 'pwd')
        ssh_tcp_port = return_input_value(datas, 'port')

        # #安装监控之前，将Monitor_Host中该用户的安装记录全部删除
        # find_user = Monitor_host.query.filter_by(user=current_user.username).all()
        # delete_dbs(find_user)


        if datas['install_system'] == 'w':
            #Windows跳转安装开始
            install_datas = {'conn_pwd': config.conn_pwd, 'monitor_url':config.monitor_url, 'userid':userid}
            ip_info,new_dict = [], {}

            for ip in ips:
                new_dict[ip] = [ssh_password, 3389]
                now_token = flush_token()
                ip_info += [[ip, datas['login_pwd'], datas['conn_proxy'], now_token]]
                insert_dbs.append(Monitor_host(ipaddr = ip,
                                               login_user = return_user(datas),
                                               login_pwd_id = return_id(Login_pwd, 'pwd', 'r_id', ssh_password),
                                               proxy_id = return_id(Proxy, 'proxy_ip', 'r_id', datas['conn_proxy']),
                                               system_id = return_id(System, 'sort_name', 'r_id', datas['install_system']),
                                               user = current_user.username,
                                               token = now_token ))
            install_datas['datas'] = ip_info
            conn_memcache.set(config.memcached_key_name(userid)[2], new_dict, 3600)
            try:
                Run_Socket_Client(install_datas, config.w_install_socket_server)
            except BaseException,e:
                write_log(path, current_user.username, e)

            #Windows跳转安装结束

        else:
            #Linux 跳转安装开始
            #为每个ip生成token
            for ip in ips:
                now_token = flush_token()
                kwargs[ip] = now_token
                insert_dbs.append(Monitor_host(ipaddr = ip,
                                        login_user = return_user(datas),
                                        proxy_id = return_id(Proxy, 'proxy_ip', 'r_id', datas['conn_proxy']),
                                        system_id = return_id(System, 'sort_name', 'r_id', datas['install_system']),
                                        user = current_user.username,
                                        token = now_token))

            kwargs['memcached_key_name'] = config.memcached_key_name(userid)[2]
            print kwargs

            #定义每种模式都传入不同形式的ssh端口号与密码
            if datas['mode'] == 'false':
                infos = [[ ip, ssh_password, ssh_tcp_port, kwargs ] for ip in ips ]
            else:
                infos = [html_datas['pwds'], html_datas['sshs'], kwargs]

            #向被监控机发送方执行命令

            try:
                #整理数据以后，将信息发送到linux跳板机实现跳转安装
                install_infos = {'conn_pwd':config.conn_pwd,'mode':datas['mode'],
                                 'ips':ips,'login_id':int(userid),
                                 'action':'install', 'infos':infos,
                                 'path':config.monitor_url}
                Run_Socket_Client(install_infos, config.monitor_check_host)
            except BaseException,e:
                write_log(path, current_user.username, e)

            #Linux跳转安装结束

        #将安装的信息写入到数据库中
        for ip in ips:
            #先冲数据库中匹配该ip是否存在，如果存在则做删除工作。
            find_ipaddr = Monitor_host.query.filter_by(ipaddr = ip).all()
            if find_ipaddr:
                delete_dbs(find_ipaddr)


        #做完删除工作后将数据再次输入到数据库中
        save_list_db(insert_dbs)

        #将添加监控的信息临时存入到memcache中，超时时间2小时
        save_data['ips'],save_data['proxy'] = ','.join(ips), datas['conn_proxy']
        conn_memcache.set(config.memcached_key_name(userid)[0], save_data, 3600)

        return redirect(url_for('main.monitor_install'))

    return render_template('monitor/monitor.html', **html_datas)

