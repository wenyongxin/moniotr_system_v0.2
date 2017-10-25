#!/usr/bin/python
#coding:utf-8


import json
import sys
import os
import re

com = "curl -s 'xfztlstatistic.efunen.com/external/query.do?m=online&areaId=18'"

result = os.popen(com).read()

result =  re.search("\[.*\]",result).group()

result = re.findall('{.*}',result)

data = {}
ol_list =[]
port_list = []
for i in result:
    info = {}
    server_id =  re.search('server_id:\d+',i).group()
    server_id = server_id.split(':')[1]
    info['serverCode'] = server_id
    online = re.search("num:'\d+'",i).group()
    online = online.split(':')[1].strip("'")
    info["onlineCnt"] = online
    for j in re.findall('\d+.\d+.\d+.\d+:\d+',i):
        port = {}
        port_info = j.split(':')
        port["IP"] = port_info[0]
        port["PORT"] = port_info[1]
        port_list.append(port)
    ol_list.append(info)

data['list'] = ol_list
data['port'] = port_list
print data