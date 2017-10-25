#!/usr/bin/env python
#ecoding:utf-8

import json, sys, urllib2, re, time
import config


reload(sys)
sys.setdefaultencoding('utf-8')

class zabbix_API():

    def __init__(self, action='application', zabbix_user=None, zabbix_password=None, zabbix_server=None):
        if action == 'test':
            self.zabbix_user = config.zabbix_user
            self.zabbix_password = config.zabbix_pwd
            self.zabbix_server = config.zabbix_server
        elif action == 'application':
            self.zabbix_user = config.zabbix_user
            self.zabbix_password = config.zabbix_pwd
            self.zabbix_server = config.zabbix_server
        elif action == 'auth' and zabbix_user and zabbix_password and zabbix_server:
            self.zabbix_password = zabbix_password
            self.zabbix_server = zabbix_server
            self.zabbix_user = zabbix_user


    def login(self):
        user_info = {'user':self.zabbix_user,'password':self.zabbix_password}
        obj = {"jsonrpc":"2.0","method":'user.login',"params":user_info,"id":0}
        json_obj = json.dumps(obj)
        content = self.postRequest(json_obj)
        try:return content['result']
        except:return False

    def postRequest(self, json_obj):
        header = {'Content-Type':'application/json-rpc','User-Agent':'python/zabbix_api'}
        url = '%s/api_jsonrpc.php' % self.zabbix_server
        request = urllib2.Request(url,json_obj,header)
        result = urllib2.urlopen(request)
        content = json.loads(result.read())
        return content


    def get_json_obj(self, method, params, auth=None):
        if auth:
            get_obj = {"jsonrpc":"2.0","method":method,"params":params,"auth":auth,"id":1}
        else:
            get_obj = {"jsonrpc":"2.0","method":method,"params":params,"auth":self.login(),"id":1}
        return json.dumps(get_obj)

    #返回结果
    def get_api_data(self, params, method, auth=None):
        get_obje = self.get_json_obj(method, params, auth)
        try:
            return self.postRequest(get_obje)['result']
        except:pass

class Efun_Zabbix(zabbix_API):

    #修改key的位置变量名称
    def change_zone_name(self, key, name):
        find_macro = re.findall(r'\$\d+', name)
        if find_macro:
            change_num = [ int(mac.strip('$')) for mac in find_macro ]
            change_list_key = re.findall(r'\[.*\]', key)[0].strip('[]').split(',')
            for zone in  change_num:
                name = name.replace('$%s' %zone, change_list_key[zone-1])
            return name
        else:
            return name

    #修改macro的名称
    def change_macro_name(self, ip):
        params = {"output": ["macro","value"], "hostids":self.get_interface_hostid(ip)}
        method = "usermacro.get"
        return self.get_api_data(params, method)

    #通过interface方式获取hostid
    def get_interface_hostid(self, ip):
        method = "hostinterface.get"
        params = {"output": "extend", "filter":{"ip":ip}}
        return self.get_api_data(params, method)[0]['hostid']


    #获取hostid
    def get_hostid(self, ip=None, auth=None):
        if ip:
            params = {"output": ['hostid','name', 'host'], "filter":{'host':ip}}
        else:
            params = {"output": ['hostid','name',"status", "groups"], "selectGroups":["groupid","name"], "filter":{'status':0}}
        method = "host.get"
        return self.get_api_data(params, method, auth)


    #用于做获取当前item的值
    def get_items(self, ip):
        try:
            hostid = self.get_hostid(ip)[0]['hostid']
            params = {
                "output":['itemid', 'key_', 'name', 'description'],
                "hostids":hostid, "filter":{'status':0, 'error':''}
            }
            method = "item.get"
            return self.get_api_data(params, method)
        except:
            return False


    #通过items的id获取对应的名称
    def get_items_names(self, items):
        params = {
                "output":["itemid", "key_", "name"],
                "itemids":items
            }
        method = 'item.get'
        return self.get_api_data(params, method)


    #通过application获取其下方的item名称
    def get_application_items(self,ip):
        params = {
            "output":"extend", "hostids":self.get_interface_hostid(ip),
            "selectItems":['itemid', 'key_', 'name'],
            "filter":{'status':0, 'error':''}
        }
        method = "application.get"
        return self.get_api_data(params, method)

    #通过itemid获取当前的值
    def get_items_value(self, items):
        params = {
            "output": ["itemid","lastvalue","key_","name"], "itemids": items,
            "filter":{"state":0}
        }
        method = 'item.get'
        return self.get_api_data(params, method)


    #通过itemid获取trigger信息
    def get_items_trigger(self, items):
        params = {
            "output":"extend",
            "itemids":items,
            "filter":{"value":1, "status":0},
            "selectItems":["itemid","status"],
            "expandDescription":""
        }
        method = 'trigger.get'
        return self.get_api_data(params, method)

    #通过hostid获取异常的trigger信息
    #value 1 为故障状态的trigger
    #status 0 开启状态的trigger
    #maintenance  True 有制作维护计划  False没有维护计划
    def get_hostids_trigger(self, hostids, auth=None, maintenance=False):
        params = {"output":["triggerid", "description", "priority", "value", "status", "lastchange"],
        # params = {"output":"extend",
                  "hostids":hostids,
                  "maintenance":maintenance,
                  "selectHosts":["hostid","status", "error", "name"],
                  "selectItems":["itemid", "lastns", "lastclock", "units", "hostid", "lifetime", "error", "history", "status", "name", "key_", "prevvalue"],
                  "selectGroups":"groupid",
                  "expandDescription":"",
                  "filter":{"value":1, "status":0}}
        method = 'trigger.get'
        return self.get_api_data(params, method, auth)

    #获取关闭报警状态，确认是否做报警关闭
    def is_ack(self, triggerids, auth=None):
        params = {
            "output":"extend",
            "objectids":triggerids,
            "select_acknowledges": "extend",
            "sortfield": ["clock", "eventid"],
            "sortorder": "DESC"
        }
        method = 'event.get'
        return self.get_api_data(params, method, auth)

    #获取user group的名称
    def get_hostgroup_name(self, search):
        params = {"output":["groupid", "name"], "search":search}
        method = 'hostgroup.get'
        return self.get_api_data(params, method)

    #获取user的完整名字以及其它信息
    def get_ures_names(self, filter):
        params = {"output":["surname", "name", "alias", "userid"], "filter":filter}
        method = "user.get"
        return self.get_api_data(params, method)


    #获取usergroup的信息
    def get_usergroup_info(self, username):
        params = {"output":["surname", "name", "alias", "userid"], "filter":filter}
        method = "user.get"
        return self.get_api_data(params, method)

    #通过hostid获取其下方有多少个graph信息
    def hostid_to_graphids(self, hostid):
        params = {"output":"extend","hostids":hostid}
        method = "graph.get"
        return self.get_api_data(params, method)


    #通过userid获取其主机组的id值
    def userid_get_groupid(self, userid):
        params = {"output":"extend", "status":0, "selectUsers":"extend", "userids":userid}
        method = "usergroup.get"
        return self.get_api_data(params, method)


    #通过itemid获取其1小时内的历史数据
    def itemid_to_history(self, itemid):

        now_time = int(time.time())
        params = {"output":"extend",
                  "itemids":itemid,
                  "time_from":now_time-60*30,
                  "time_till":now_time,
                  "sortfield": "clock",
                  "sortorder": "DESC",
                  "limit": 10}

        method = "history.get"
        for hi in [0, 1, 2, 3, 4]:
            params['history'] = hi
            data = self.get_api_data(params, method)
            if data:
                return data






if __name__=='__main__':
    a = Efun_Zabbix()
    print 'x'*40
    print a.itemid_to_history('27650')