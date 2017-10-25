#!/usr/bin/env python
#ecoding:utf-8

import time
from datetime import datetime

#按照年-月-日 小时:分钟格式返回
#通过传递时间格式。返回对应的格式信息
#%Y-%m-%d %H:%M:%S  年-月-日 小时：分钟：秒
def date_time(format='%Y-%m-%d %H:%M'):
    return time.strftime(format,time.localtime(time.time()))


#时间戳转换成日期格式
def strftime_to_date(strftime, format='%Y-%m-%d %H:%M'):
    return time.strftime(format,time.localtime(strftime))


#日期转换成时间戳
def date_to_strftime(date):
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M")
    return int(time.mktime(timeArray))

#数据库中datetime格式数据转换成字符串
def db_datetime_string(a, format='%Y-%m-%d %H:%M:%S'):
    return time.strftime(format, a.timetuple())


#将时间戳转换成datetime格式数据
def strftime_to_datetime(strftime):
    return datetime.fromtimestamp(int(strftime))