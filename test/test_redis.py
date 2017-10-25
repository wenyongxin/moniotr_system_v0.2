#!/usr/bin/env python
#ecoding:utf-8

import config
import redis
from app.scripts.zabbix import Efun_Zabbix


__redis = redis.StrictRedis(host=config.redis_config.host,
        port=config.redis_config.port,
        password=config.redis_config.password
    )


# __redis.rpush('123','abc')
# print __redis.lrange('123', start=0, end=-1)
# __redis.rpush('123','def')
print config.flush_frequency.data_range / config.flush_frequency.everyone_flush
print __redis.lrange('efun_time_range', start=0, end=-1)
print __redis.llen('efun_time_range')
print '*'*50
print __redis.lrange('386276', start=0, end=-1)
print __redis.llen('386276')
print '*'*50
print __redis.lrange('386365', start=0, end=-1)
print __redis.llen('386365')
print '*'*50
print __redis.lrange('331859', start=0, end=-1)
print __redis.llen('331859')
print '*'*50

#
# __redis.set('aaa',{'a':1,'b':2})
# print __redis.get('aaa')

# zabbix = Efun_Zabbix()
#
# items = '386276,386277,386278,386279,386280,386281,386282'
#
# print zabbix.get_items_trigger(items.split(','))