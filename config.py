#ecoding:utf-8
import os,time
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))

#部门列表名称
department = {1:u'管理部', 2:u'运维部', 3:u'开发部', 4:u'运营'}
status_list = {0 :u'启用', 1 :u'禁用'}

#默认登录密码
default_login_passwd = '123456'

#公司运营中心
efun_centers = {1:u'港台中心', 2:u'亚欧中心', 3:u'韩国中心', 4:u'国内中心'}

#################################### 企业ＱＱ　ＡＰＩ配置文件 开始##########################################################
#企业QQ相关信息
class company_qq:
    oauth_version = '2'
    app_id = 'xxxxxxxxxxx'
    company_id = 'xxxxxxxxxxxxxxx'
    company_token = 'xxxxxxxxxxxxxx'
    open_id = 'xxxxxxxxxxxxxxx'
    client_ip = '203.69.109.124'
    #获取企业Q列表信息
    user_list_url = 'http://openapi.b.qq.com/api/user/list'
    #获取用户资料
    user_info = 'https://openapi.b.qq.com/api/user/info'
    #获取用户邮箱地址
    user_email = 'https://openapi.b.qq.com/api/user/email'
    #获取用户手机号
    user_telphone = 'https://openapi.b.qq.com/api/user/mobile'

company_qq_get_data = {
            "oauth_version" : company_qq.oauth_version,
            "app_id" : company_qq.app_id,
            "company_id" : company_qq.company_id,
            "company_token" : company_qq.company_token,
            "open_id" : company_qq.open_id,
            "client_ip" : company_qq.client_ip
        }
#命名用于存储在memcached中。方便其它程序直接调用处理
save_user_list_dict = 'user_list'

#########################################企业ＱＱ　ＡＰＩ配置文件 结束　##################################################



#Mysql配置文件信息
dbuser = 'root'
dbpasswd = '0new0rd'
dbhost = '172.16.5.230'
# dbhost = 'localhost'
dbport = '3306'
db = 'monitor'

#socket连接验证密码
conn_pwd = '0new0rd'

#windows监控安装连接服务器地址
w_install_socket_server = '172.16.5.246'
w_install_socket_port = 8082

#监控安装完毕后做相应的检测
monitor_check_host = '172.16.5.240'
monitor_check_port = 8082

#监控系统地址
#monitor_url = '172.16.15.255:9090'

#监控系统地址（正式环境）
#monitor_url = '172.16.120.81:9090'

#测试环境
monitor_url = '172.16.5.5'


#zabbix server API连接信息
zabbix_server = 'http://172.16.5.240/zabbix'
zabbix_user = 'efun'
zabbix_pwd = 'p@ssw0rd'

#返回存储在memcached中的名称
def memcached_key_name(userid):
    save_memcache_key = '%s_monitor_ips' %userid
    message_key = '%s_message_key' % userid
    ok_ips_key = '%s_ok_ips' % userid
    return (save_memcache_key, message_key, ok_ips_key)

#连接memcached
def conn_memcached():
    import memcache
    # mc = memcache.Client(['172.16.5.240:11211'], debug=0)
    # mc = memcache.Client(['localhost:11211','172.16.5.240:11211'], debug=0)
    mc = memcache.Client(['localhost:11211'], debug=0)
    return mc

#redis配置文件
class redis_config:
    host = '172.16.5.230'
    port = 6379
    password = ''


#数据获取频率
class flush_frequency:
    everyone_flush = 2*60
    data_range = 60 * 60 * 24

#redis中时间列表的名称
time_name = 'efun_time_range'



#防止csrf攻击，字符串要固定值
SECRET_KEY = 'kmFwZ4NiQ0dreBhRpM9CK289AaKRDuej'
# SECRET_KEY = os.urandom(24)
SQLALCHEMY_TRACK_MODIFICATIONS = True


SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' %(dbuser, dbpasswd, dbhost, dbport, db)


####################################### celery 配置文件开始 ######################################################
CELERY_BROKER_URL='redis://localhost:6379/0'
#结果存储地址
CELERY_RESULT_BACKEND='redis://localhost:6379/0'
#存储日志路径
CELERYD_LOG_FILE = os.path.join(basedir,'logs','celery_logs_%s.log' %time.strftime("%Y-%m-%d", time.localtime()))
#任务序列化josn格式存
CELERY_TASK_SERIALIZER = 'json'
#结果序列化json格式
CELERY_RESULT_SERIALIZER = 'json'
#celery接收内容类型
CELERY_ACCEPT_CONTENT = ['json']
#celery任务结果有效期
CELERY_TASK_RESULT_EXPIRES = 3600
#设置celery的时区
CELERY_TIMEZONE='Asia/Shanghai'
#启动时区设置
CELERY_ENABLE_UTC = True
#定义celery的路由
# CELERY_ROUTES = {
#         'tasks.get_zabbix_date':{'queue':'for_add', 'routing_key':'for_add'}
# }

#显示任务速率
#CELERY_ANNOTATIONS = {
#       'celerys.add':{'rate_limit':'10/m'}
#}

#定义每2分钟执行一次
CELERYBEAT_SCHEDULE = {
        "get_zabbix_date":{
                'task':'tasks.get_zabbix_date',
                'schedule':timedelta(seconds=flush_frequency.everyone_flush),
                'args':()
        },
}
####################################### celery 配置文件结束 ######################################################

