#!/usr/bin/env python
#ecoding:utf-8

from manage import celery
from app.business.models import Manager_business, History_Number, History_String
import time, config
from app.scripts.tools import save_list_db
from app.scripts.redis_manage import Efun_Redis
from app.scripts.zabbix_manage import manage_zabbix
from app.scripts.time_manage import date_time

#全局变量
zabbix = manage_zabbix()

#通过从数据库中获取全部的items的信息
def return_all_items():
    all_items = []
    #任务计划，获取item对应的值
    business = Manager_business.query.all()
    for bus in business:
        all_items += bus.items.split(',')
    all_items = list(set(all_items))
    return all_items


def items_data(now_time):
    save_datas = []
    datas = zabbix.get_items_value(return_all_items())
    #将时间存储到redis中
    Efun_Redis.redis_save_list(config.time_name, now_time)
    for data in datas:
        #保存到数据库中
        history = History_Number(itemid=data['itemid'], datetime=now_time, value=float(data['lastvalue']))
        save_datas.append(history)
        #保存到redis
        Efun_Redis.redis_save_list(data['itemid'], float(data['lastvalue']))
    #保存到数据库中
    save_list_db(save_datas)



def triggers_data(now_time):
    save_datas = []
    datas = zabbix.get_items_trigger(return_all_items())
    if datas:
        for data in datas:
            history = History_String(itemid=data['itemid'], datetime=now_time, value=data['description'])
            save_datas.append(history)
        save_list_db(save_datas)

@celery.task
def get_zabbix_date():
    now_time = date_time()
    items_data(now_time)
    triggers_data(now_time)


