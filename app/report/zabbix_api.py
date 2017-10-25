#!/usr/bin/python
#coding:utf-8

import json
import urllib2
import sys
import re
import time
import MySQLdb

reload(sys)
sys.setdefaultencoding("utf-8")

time = str(time.time())
time = time.split('.')[0]



class ZabbixAPI(object):
    auth = ''
    id = 0

    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password

    def login(self):
        user_info = {'user': self.user, 'password': self.password}
        obj = self.json_obj('user.login', user_info)
        content = self.postRequest(obj)
        self.auth = content['result']

    def json_obj(self, method, params):
        obj = {"jsonrpc": "2.0", "method": method, "params": params, "id": self.id}
        return json.dumps(obj)

    def postRequest(self, json_obj):
        header = {'Content-Type': 'application/json-rpc', 'User-Agent': 'python/zabbix_api'}
        request = urllib2.Request(self.url, json_obj, header)
        result = urllib2.urlopen(request)
        content = json.loads(result.read())
        self.id += 1
        return content


class Handle(ZabbixAPI):
    def __init__(self, url, user, password, params, method):
        ZabbixAPI.__init__(self, url, user, password)
        self.params = params
        self.method = method

    def get_json_obj(self, method, params):
        get_obj = {"jsonrpc": "2.0", "method": method, "params": params, "auth": self.auth, "id": self.id}
        return json.dumps(get_obj)

    def handle(self):
        get_obj = self.get_json_obj(self.method, self.params)
        get_content = self.postRequest(get_obj)
        return get_content


def main(url, user, password, params, method):
    zapi = Handle(url, user, password, params, method)
    zapi.login()
    result = zapi.handle()
    return result


def get_data(url, user, password, params, method):
    result = main(url, user, password, params, method)
    return result['result']





url = 'http://zabbix.efuntw.com/zabbix/api_jsonrpc.php'
#url = 'http://218.32.219.219/zabbix/api_jsonrpc.php'
#url = 'http://172.16.60.202/zabbix/api_jsonrpc.php'


user = 'username'
password = 'password'








params = {
              "output": ['maintenanceid','name','maintenance_type','active_since','active_till'],
              "selectGroups": ['groupid','name'],
              "selectTimeperiods": "extend",
              "selectHosts":['hostid','name'],
               }
method = "maintenance.get"

data = get_data(url, user, password, params, method)
for i in data:
    try:
        print i['name'],i['name'],i['timeperiods'][0]['dayofweek']
    except:
        print i['name'], i['name'], i['timeperiods'][0]['dayofweek']