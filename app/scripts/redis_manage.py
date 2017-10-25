#!/usr/bin/env python
#ecoding:utf-8

from redis import StrictRedis
import sys
sys.path.append('../..')
import config


class Efun_Redis():

    __redis = StrictRedis(
            host=config.redis_config.host,
        port=config.redis_config.port,
        password=config.redis_config.password
    )

    #普通的获取方式
    @classmethod
    def redis_get(cls, key):
        return cls.__redis.get(key)

    #普通的读取方式
    @classmethod
    def redis_set(cls, key, value, timeout=60*60):
        return cls.__redis.set(key, value, timeout)

    #获取列表的长度
    @classmethod
    def redis_len(cls, key):
        return cls.__redis.llen(key)

    #列表修剪
    @classmethod
    def redis_ltrim(cls, key, start):
        return cls.__redis.ltrim(key, start=int(0-start+1), end=-1)


    #列表向右侧添加数据
    @classmethod
    def redis_rpush(cls, key, value):
        return cls.__redis.rpush(key, value)

    #读取列表
    @classmethod
    def redis_lrange(cls, key, start=0, end=-1):
        return cls.__redis.lrange(key, start=start, end=end)




    #1、判断列表是否存在
    #2、如果不存在则创建
    #3、如果存在则获取该列表计算长度
    #4、如果长度与配置文件的要求相同则移除最左侧的一个数据，在最右侧加上数据。保证数据的长度与配置文件中要求相同
    #5、处理ok后。替换当前redis中的值
    @classmethod
    def redis_save_list(cls, key, value):

        if cls.redis_lrange(key):
            data_range = config.flush_frequency.data_range / config.flush_frequency.everyone_flush
            if cls.redis_len(key) == data_range or cls.redis_len(key) > data_range:
                cls.redis_ltrim(key, data_range)
                cls.redis_rpush(key, value)
            else:
                cls.redis_rpush(key, value)
                cls.redis_lrange(key)

        else:
            cls.redis_rpush(key, value)
            cls.redis_lrange(key)





