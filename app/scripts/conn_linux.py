#!/usr/bin/env python
#ecoding:utf-8


#################################################################
# ---------------本脚本功能用途：-----------------
# 1、通过传参确定ssh远程连接的tcp端口与ssh密码是不是需要自动匹配
# 2、如果输入的是手动输入了ssh的端口与登录密码，则直接安装
# 3、如果是选择自动的话，则需要在后台运行做匹配。
# 编写日期：2016年12月15日
# 编写人：温永鑫 007
# 编写版本：V2,0
#################################################################


import paramiko, sys, os, time
from multiprocessing import Process, Queue
from tools import flush_token, random_num, save_memcached_list
sys.path.append('../..')
import config



reload(sys)
sys.setdefaultencoding('utf8')




#通过paramiko模块做ssh登录检测，用于匹配密码
#def Find_ssh_Pwd(hostname, password, port, cmd):
def Install_Monitor(hostname, password, port, cmd):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname, username="root", password=password, port=int(port))
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()
    except StandardError,e:
        pass
    finally:
        ssh.close()



#通过paramiko 进行sft发送数据
def Send_File(hostname, password, port, pwd, kwargs, mode):
    install_cmd = r'chmod a+x /root/%s && /root/%s %s %s %s %s %s %s %s' %(kwargs['filename'], kwargs['filename'], kwargs['system'], hostname, kwargs['proxy'], kwargs[hostname], config.monitor_url, random_num(), kwargs['user_id'])
    try:
        t = paramiko.Transport((hostname, int(port)))
        t.connect(username="root", password=password)
        sftp = paramiko.SFTPClient.from_transport(t)

        remote_dir = "/root/%s" % kwargs['filename']
        local_dir = r'%s/app/static/files/monitor_install/%s' %(pwd, kwargs['filename'])

        if sftp.put(local_dir,remote_dir):
            new_dict = {hostname:[password, port]}
            save_memcached_list(config.memcached_key_name(kwargs['user_id'])[2], new_dict)
            Install_Monitor(hostname, password, port, install_cmd)
        t.close()
    except:
        pass




#通过多进程模块multiprocessing 做快速匹配
def Multi_ssh_infos(infos, ips, pwd, mode='false'):
    process = []

    for info in infos:
        process.append(Process(target=Send_File, args=(info[0], info[1], info[2], pwd, info[3], mode)))


    for p in process:
        p.start()


#flsk导入的模块接口
def Install_Start(mode, infos, ips, pwd, userid):
    #手动为false   自动为 true
    #kwargs = {'filename':'install-agent.V2.0.sh', 'system':'c', 'proxy':'103.227.128.16'}
    # filename  监控安装脚本名称
    # system 系统名称 c
    # proxy IP地址
    # 当前host 的token
    # pwd 传回的目录结构 /usr/local/monitor/moniotr_system


    if mode == 'false':
        Multi_ssh_infos(infos, ips, pwd)
    else:
        new_infos =  [[ip, password, port, infos[2]] for ip in ips for password in infos[0] for port in infos[1]]
        Multi_ssh_infos(new_infos, ips, pwd, 'true')



#执行脚本用于测试
if __name__ == '__main__':
	#ips = ['172.16.5.240', '172.16.5.243']
	ips = ['172.16.5.243', '172.16.5.240', '172.16.5.15', '172.16.5.241']
	ports = [20755, 36000, 22]
	passwords = ['0new0rd', 'p@ssw0rd', '#uu&)+?SSj#K_06', 'Efun@168', 'Efun@169']
	pwd = r'/usr/local/monitor/moniotr_system'

	kwargs = {'filename':'install-agent.V2.0.sh', 'system':'c', 'proxy':'103.227.128.16'}
	for ip in ips:
		kwargs[ip] = flush_token()

	infos = [ [ip, password, port, pwd, kwargs ] for ip in ips for password in passwords for port in ports ]
	Multi_ssh_infos(infos, ips, pwd, mode='false')









