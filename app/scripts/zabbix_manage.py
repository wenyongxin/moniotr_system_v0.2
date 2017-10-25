#!/usr/bin/env python
#ecoding:utf-8


from zabbix import Efun_Zabbix
from ..scripts.tools import save_memcache_value,get_memcached_value
from ..business.models import Manager_business
import string, json, re, urllib, urllib2, cookielib, sys
from ..models import Sections,db
from redis_manage import Efun_Redis
from multiprocessing import Process
sys.path.append('../..')
import config, time


class zabbix_tools():

    @classmethod
    def return_sections(cls):
        all_centers = db.session.query(Sections).filter(Sections.name.like('%中心')).all()
        all_data = {}
        for center in all_centers:
            all_urls = Sections.query.filter_by(membership=center.id).all()
            all_data.update({'0':center.name})
            all_data.update({ i.id: '%s %s' %(i.name, i.href) for i in all_urls})

        return all_data

    @classmethod
    def return_db_items(cls, ip):
        return Manager_business.query.filter_by(hostip = ip).first()

    @classmethod
    def return_sort(cls):
        return { n:i for n,i in enumerate(list(string.ascii_letters))}




class manage_zabbix(Efun_Zabbix):

    #判断checkbox是否为选中状态
    def is_checked(self, item, items):
        if int(item['itemid']) in items:
            item['type'] = True
        else:
            item['type'] = False
        return item

    #判断导航栏下面的checkbox是否有选中？如果有选中则该名称
    def show_is_checked(self, new_items, application_name, new_datas):
        if True in [ b['type'] for b in new_items ]:
            if 'is_check' not in application_name:
                new_name = '%s (is_check)' %application_name
            else:
                new_name = application_name
        else:
            new_name = application_name
        new_datas[new_name] = new_items
        return new_datas


    #整合zabbix的名称，防止因为macro导致名称显示异常现象
    def get_zabbix_host_infos(self, ip, check_items):
        new_datas = {}
        host_macros = { i['macro']:i['value'] for i in self.change_macro_name(ip) }
        for application in self.get_application_items(ip):
            items, new_items = application['items'], []
            if items:
                for item in items:
                    item['name'] = self.change_zone_name(item['key_'], item['name'])
                    find_macro = re.findall(r'\{\$.*\}', item['name'])
                    item = self.is_checked(item, check_items)
                    if find_macro:
                        for macro_key in host_macros.keys():
                            if macro_key in '.'.join(find_macro):
                                item['name'] = item['name'].replace(macro_key, host_macros[macro_key])
                    new_items.append(item)

            if application['items']:
                new_datas = self.show_is_checked(new_items, application['name'], new_datas)
                new_datas['checked_items'] = check_items
        return new_datas


    #处从memcached中读取的数据。用于对checkbox做选中状态
    def checkbox_checked(self, all_data, items):
        new_datas = {}
        for application_name, host_items in all_data.items():
            if application_name != 'checked_items':
                new_items = []
                for item in host_items:
                    new_items.append(self.is_checked(item, items))
                new_datas = self.show_is_checked(new_items, application_name, new_datas)
            else:
                new_datas['checked_items'] = items

        return new_datas


    #整理zabbix信息。该整理的结果能够自动选中以及以及目录上做标识
    #1、从memcached中查找返回的字符串是否存在。
    #2、如果存在则读取memcached中的信息
    #3、如果不存在则运行get_zabbix_host_infos() 方法，并将返回信息存放在memcached中
    #4、存放要求，key以ip命名，存储时间10分钟 60*10
    def return_views_info(self, ip, check_items=[], select=False):
        if ip:
            if get_memcached_value(ip):
                new_datas = get_memcached_value(ip)
            else:
                new_datas = self.get_zabbix_host_infos(ip, check_items)
                save_memcache_value(ip, new_datas, 10*60)

            if select:
                #用于判断数据库中的items与memcached中记录的items是否相同。如果不同则进行处理更新memcached
                memcached_data = new_datas['checked_items']
                memcached_data.sort()

                if memcached_data != check_items:
                    new_datas = self.checkbox_checked(new_datas, check_items)

            return new_datas
        else:
            return {}


    #缓存itemid对应的名称，通过开启对应的页面做第一次缓存。缓存以后不再更改
    #缓存到redis，永久保存。判断方式。redis的key名，当前页面的名称。
    #通过判断item的数量。有没有变动。确认是否更新缓存。如果不相等则更新缓存

    def zabbix_items_names(self,value):
        new_items = {}
        for line in self.get_items_names(value):
            new_items[line['itemid']] = self.change_zone_name(line['key_'], line['name'])
        return json.dumps(new_items)


    def items_names(self, key, items):
        get_redis_datas = Efun_Redis.redis_get(key)
        if get_redis_datas:
            get_redis_datas = json.loads(Efun_Redis.redis_get(key))
            if len(get_redis_datas.keys()) != len(items):
                Efun_Redis.redis_set(key, self.zabbix_items_names(items), 0)
        else:
            Efun_Redis.redis_set(key, self.zabbix_items_names(items), 0)

        return json.loads(Efun_Redis.redis_get(key))


    #通过历遍的方式获取制定名称的主机组信息，并返回成一个完整的列表格式
    #从memcached中读取，如果读取失败则通过api刷新获取。
    #刷新成功则再次保存在API中，缓存失效1个小时
    def find_hostgroup_names(self, names):
        get_info = get_memcached_value('center_hostgroup_name')
        if get_info:
            return get_info
        else:
            all_datas = {}
            for name in names:
                search = {'name':name}
                all_datas[name.strip('_')] = { int(i['groupid']):i['name'] for i in self.get_hostgroup_name(search) }

            save_memcache_value('center_hostgroup_name', all_datas, 60*60*12)
            return all_datas

    #返回游戏负责人名称列表
    def find_op_users(self):
        filter = {"name":u'游戏运维'}
        get_user_info = get_memcached_value('op_users')
        if get_user_info:
            return get_user_info
        else:
            save_mem = { line['surname'].split(":")[0]:line['surname'].split(":")[1] for line in self.get_ures_names(filter)}
            save_memcache_value('op_users', save_mem, 60*60*12)
            return save_mem


    #返回当前报警trigger是否被关闭报警
    def return_trigger_ack_info(self, triggerid, auth):
        from ..scripts.time_manage import strftime_to_datetime

        try:
            all_ack = [ ack['acknowledges'] for ack in self.is_ack(triggerid, auth) ]
            if all_ack[0]:
                line = all_ack[0][0]
                ack_message = "%s|%s|%s" %(line['alias'], strftime_to_datetime(line['clock']), line['message'])
                save_memcache_value(triggerid, ack_message, 60*10)
        except BaseException,e:
            pass



    #通过多进程方式快速的调用返回当前项目是否已经被关闭报警
    def multi_get_ack(self, triggerids, auth):
        process = []
        for triggerid in triggerids:
            process.append(Process(target=self.return_trigger_ack_info, args=(triggerid, auth)))

        for p in process:
            p.start()


    #做zabbix的cooice的缓存
    def download_zabbix_image(self, user_info):

        #模拟登陆生成cookle生成cookle

        login_opt = urllib.urlencode({"name":user_info['user'],"password":user_info['password'],"autologin":1,"enter":"Sign in"})
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        login_url = r"%s/index.php" % config.zabbix_server
        opener.open(login_url,login_opt).read()

        return opener

    #通过itemid的方式获取图片的二进制代码
    def return_item_graph(self, auth, itemid):

        user_info = get_memcached_value(auth)
        #下载图片信息
        get_graph_opt = urllib.urlencode({"sid":user_info['sid'],"period":"3600", "action":'showgraph',"itemids[]":itemid})
        save_graph_url = r"%s/chart.php" % config.zabbix_server
        data = self.download_zabbix_image(user_info).open(save_graph_url,get_graph_opt).read()

        return data


    #通过graphid的方式过去汇总的graph信息
    def return_graphid_graph(self, auth, graphid):

        user_info = get_memcached_value(auth)
        stime = int(time.time()) - 3600
        get_graph_opt = urllib.urlencode({"graphid":graphid, "period":"3600", "stime":stime})
        save_graph_url = r"%s/chart2.php" % config.zabbix_server
        data = self.download_zabbix_image(user_info).open(save_graph_url,get_graph_opt).read()

        return data


    #用于修改当前主机中的macro以及位置变量的信息
    def change_all_macro_name(self, itemid, ip):

        #目前已经将位置变量名字更新
        now_item_info = self.get_items_names(itemid)[0]
        new_name = self.change_zone_name(now_item_info['key_'], now_item_info['name'])


        #更新macro的名字
        macros_host = { m['macro']:m['value'] for m in self.change_macro_name(ip) }
        if macros_host:
            for macro in re.findall(r'\{\$.*\}', now_item_info['name']):
                new_name = new_name.replace(macro, macros_host[macro])
                print new_name
        return new_name

