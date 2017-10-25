#!/usr/bin/env python
#ecoding:utf-8
from datetime import datetime
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
from flask import request


#权限级别
class Permission:
    administrator = 0xff    #管理员完全控制
    user = 0x06             #user部分可控
    # guest = 0x01            #guest来宾



class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)                    #名称
    default = db.Column(db.Boolean, default=False, index=True)      #设定该权限是否为默认
    permissions = db.Column(db.Integer)                             #权限值
    name_cn = db.Column(db.String(64))                              #中文名称
    describe = db.Column(db.String(64))                             #描述
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        #这里设置的True为创建账号过程中默认的权限。此处设置为guest具有只读权限
        roles = {
            # 'guest': (Permission.guest, False, u'来宾', u'只读'),
            'user': (Permission.user, True, u'普通用户', u'读写操作'),
            'Administrator': (Permission.administrator, False, u'超级管理员', u'完全控制')
        }
        '''
        在命令行中执行更新权限表
        (env_win) D:\efun\monitor\moniotr_system_v0.2>python manage.py shell
        In [1]: from app.models import Role
        In [2]: Role.insert_roles()
        In [3]: Role.query.all()
        Out[3]: [<Role u'Administrator'>, <Role u'guest'>, <Role u'user'>]
        '''
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            role.name_cn = roles[r][2]
            role.describe = roles[r][3]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)               #注册邮箱地址
    username = db.Column(db.String(64), unique=True, index=True)            #用户名称
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))              #权限外键
    password_hash = db.Column(db.String(128))                               #加密密码
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)        #创建日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)           #最后一次登录时间
    department = db.Column(db.String(64))                                   #部门
    telphone = db.Column(db.String(11))                                     #手机号
    status = db.Column(db.Boolean, default=False)                           #用于判断是否被禁用。true为禁用。false启用状态
    avatar = db.Column(db.String(64), default="default.jpg")                #头像图片默认为default.jpg

    #与Users表实现一对多
    permission_id = db.Column(db.Integer, db.ForeignKey('permission_model.id'))
    user_table = db.relationship('Permission_Model', backref='users')


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        #此处配置role_id对应的默认的权限
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    #返回密码错误信息
    @property #将方法变成属性
    def password(self):
        raise AttributeError('password is not a readable attribute')

    #将明文密码做hash加密
    @password.setter #把password设置为set方法
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    #密码校验
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #返回默认密码
    def default_password(self):
        from config import default_login_passwd
        return default_login_passwd

    #用于确认用户权限
    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    #默认不传则走self方式判断。
    #传参数则判断是不是管理员
    def is_admin(self, sesctionid=None):
        if sesctionid:
            if int(sesctionid) == 1:
                return True
            else:
                return False
        else:
            if int(self.permission_id) == 1:
                return True
            else:
                return False


    #返回当前用户的id
    def is_me(self):
        return self.id


    #返回zabbix验证后的key名称
    def zabbix_user_key(self):
        return '%s_auth' %self.id

    #用于判断是否有查看当前url路径的权限
    def show_sections(self):
        es = db.session.query(Permission_Model).filter_by(id = self.permission_id).first()
        for i in es.section:
            if i.href.encode('utf-8') == request.path:
                return True


    #通过将信息渲染到current_user中，实现在前端中能够显示导航栏显示
    def sesctions(self, sesctionid=None):
        sections_list = []
        if self.is_admin(sesctionid):
            #这里的id 1 为超级管理员，只要在版块管理中有路径添加都会实现全部显示
            sections = db.session.query(Sections).filter(Sections.head==1,Sections.membership==None).order_by(Sections.href).all()
            for a in sections:
                infos = db.session.query(Sections).filter(Sections.membership==a.id).all()
                sections_list.append({'section':a, 'urls':infos})
        else:
            #这里按照获取用户的权限id permission方式。来确认当前都有查看那些版块的权限
            #1 先筛选出当前权限id的对应编号
            if not sesctionid:
                sesctionid = self.permission_id

            res = Permission_Model.query.filter_by(id = sesctionid).first()
            #2 找出版块名称
            sectionss = []
            for f_sections in res.section:
                if f_sections.head and f_sections.membership == None:
                    sectionss.append(f_sections)

            #3 通过匹配id与membership是否相同。如果相同则对方称一个列表
            for f_urls in sectionss:
                local_urls = []
                for f_sections in res.section:
                    if f_urls.id == f_sections.membership:
                        local_urls.append(f_sections)
                sections_list.append({'section':f_urls, 'urls':local_urls})
        return sections_list

    def __repr__(self):
        return '<User %r>' % self.username



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#远程主机系统登录密码表
class Login_pwd(db.Model):
    __tablename__='login_pwd'
    id = db.Column(db.Integer, primary_key=True)
    pwd = db.Column(db.String(64), unique=True)
    prob = db.Column(db.Integer)

    def __repr__(self):
        return '<Login_pwd %s>' % self.pwd


#远程主机SSH端口列表
class Login_ssh(db.Model):
    __tablename__='login_ssh'
    id = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer, unique=True)
    prob = db.Column(db.Integer)

    def __repr__(self):
        return '<Login_ssh %s>' % self.port


#存储proxy信息
class Proxy(db.Model):
    __tablename_='proxy'
    id = db.Column(db.Integer, primary_key=True)
    proxy_name = db.Column(db.String(64), unique=True)
    proxy_ip = db.Column(db.String(64), unique=True)
    proxy_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Proxy %s %s %s>' %(self.proxy_name, self.proxy_ip, self.proxy_ip)


#存储操作系统表
class System(db.Model):
    __tablename__='system'
    id = db.Column(db.Integer, primary_key=True)
    sort_name = db.Column(db.String(64), unique=True)
    full_name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<System %s %s>' %(self.sort_name, self.full_name)



#记录添加监控主机的信息
class Monitor_host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ipaddr = db.Column(db.String(64))
    login_user = db.Column(db.String(64))
    login_pwd_id = db.Column(db.Integer, db.ForeignKey('login_pwd.id'))
    login_pwd = db.relationship('Login_pwd', backref=db.backref('login_pwd', lazy='dynamic'))
    login_ssh_id = db.Column(db.Integer, db.ForeignKey('login_ssh.id'))
    login_ssh = db.relationship('Login_ssh', backref=db.backref('login_ssh', lazy='dynamic'))
    proxy_id = db.Column(db.Integer, db.ForeignKey('proxy.id'))
    proxy = db.relationship('Proxy', backref=db.backref('proxy', lazy='dynamic'))
    system_id = db.Column(db.Integer, db.ForeignKey('system.id'))
    system = db.relationship('System', backref=db.backref('system', lazy='dynamic'))
    user =  db.Column(db.String(64))
    time = db.Column(db.DateTime(), default=datetime.now)
    finsh = db.Column(db.Boolean, default=False)
    check_status = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(10))

    def __repr__(self):
        return '<Monitor_host %s>' %self.id



#图标表
class Icon(db.Model):

    __tablename__='icon'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    icon_name = db.Column(db.String(64), unique=True)
    sections = db.relationship('Sections', uselist=False)


    def __repr__(self):
        return '<Icon:%s>' %self.icon_name




permissions_sections = db.Table('permissions_sections',
                                db.Column('permissions_id', db.Integer, db.ForeignKey('permission_model.id'), primary_key=True),
                                db.Column('sections_id', db.Integer, db.ForeignKey('sections.id'), primary_key=True)
                                )



#User对应section权限的管理
class Permission_Model(db.Model):

    __tablename__='permission_model'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)                #id
    name = db.Column(db.String(64), unique=True)                                    #名称
    describe = db.Column(db.String(128), unique=True)                               #描述
                                                                                    #Permission_Model表为多
    section = db.relationship('Sections', secondary=permissions_sections)

    def __repr__(self):
        return '<Section_Url_Info:%s>' %id


#导航条信息
class Sections(db.Model):

    __tablename__='sections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #一对一的外键
    icon_id = db.Column(db.Integer, db.ForeignKey('icon.id'))       #图标的id值。一对第一关系
    icon = db.relationship('Icon')

    name = db.Column(db.String(64), nullable=False, unique=True)    #标题名称
    href = db.Column(db.String(128), nullable=False, unique=True)   #链接地址
    head = db.Column(db.Boolean, default=False)                     #是否为头部信息
    membership = db.Column(db.Integer)                              #隶属于那个节点之下。传入id

    describe = db.Column(db.String(128))                            #描述信息

    permission = db.relationship('Permission_Model', secondary=permissions_sections)

    business = db.relationship('Manager_business')

    def __repr__(self):
        return '<Sections:%s>' %self.id




#################################################report######################################################

class Trouble_repo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trouble_date = db.Column(db.String(64), index=True)
    operating_center = db.Column(db.String(64), index=True)
    business_module = db.Column(db.String(64), index=True)
    trouble_affair = db.Column(db.String(256), index=True)
    affect_scope = db.Column(db.String(256), index=True)
    isnot_inner = db.Column(db.String(32), index=True)
    affect_time = db.Column(db.String(32), index=True)
    isnot_experience = db.Column(db.String(32), index=True)
    affect_user = db.Column(db.String(32), index=True)
    affect_money = db.Column(db.String(32), index=True)
    data_source = db.Column(db.String(32), index=True)
    isnot_core = db.Column(db.String(32), index=True)
    trouble_type = db.Column(db.String(64), index=True)
    heading_user = db.Column(db.String(64), index=True)
    trouble_attr = db.Column(db.String(64), index=True)
    trouble_status = db.Column(db.String(64), index=True)
    trouble_cause = db.Column(db.String(512), index=True)
    whith_process = db.Column(db.String(1024), index=True)
    lesson_course = db.Column(db.String(512), index=True)
    improve = db.Column(db.String(512), index=True)
    repo_date = db.Column(db.String(64), index=True, default=time.strftime('%Y-%m-%d',time.localtime(time.time())))

    def __repr__(self):
        return 'trouble_date %r' % self.trouble_date


class Trouble_repo_add(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trouble_date = db.Column(db.String(64), index=True)
    operating_center = db.Column(db.String(64), index=True)
    business_module = db.Column(db.String(64), index=True)
    trouble_affair = db.Column(db.String(256), index=True)
    affect_scope = db.Column(db.String(256), index=True)
    isnot_inner = db.Column(db.String(32), index=True)
    affect_time = db.Column(db.String(32), index=True)
    isnot_experience = db.Column(db.String(32), index=True)
    affect_user = db.Column(db.String(32), index=True)
    affect_money = db.Column(db.String(32), index=True)
    data_source = db.Column(db.String(32), index=True)
    isnot_core = db.Column(db.String(32), index=True)
    trouble_type = db.Column(db.String(64), index=True)
    heading_user = db.Column(db.String(64), index=True)
    trouble_attr = db.Column(db.String(64), index=True)
    trouble_status = db.Column(db.String(64), index=True)
    trouble_cause = db.Column(db.String(512), index=True)
    whith_process = db.Column(db.String(1024), index=True)
    lesson_course = db.Column(db.String(512), index=True)
    improve = db.Column(db.String(512), index=True)
    add_date = db.Column(db.String(64), index=True, default=time.strftime('%Y-%m-%d', time.localtime(time.time())))

    def __repr__(self):
        return 'trouble_date %r' % self.trouble_date



class Month_trouble_repo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trouble_date = db.Column(db.String(64), index=True)
    operating_center = db.Column(db.String(64), index=True)
    business_module = db.Column(db.String(64), index=True)
    isnot_inner = db.Column(db.String(32), index=True)
    affect_time = db.Column(db.String(32), index=True)
    isnot_experience = db.Column(db.String(32), index=True)
    isnot_core = db.Column(db.String(32), index=True)
    trouble_type = db.Column(db.String(64), index=True)
    trouble_attr = db.Column(db.String(64), index=True)

    def __repr__(self):
        return 'trouble_date %r' % self.trouble_date


class Month_trouble_log(db.Model):
    trouble_month = db.Column(db.String(32), index=True, primary_key=True)
    trouble_time_AE_login_core = db.Column(db.Integer, index=True)
    trouble_time_AE_store_core = db.Column(db.Integer, index=True)
    trouble_time_AE_register_core = db.Column(db.Integer, index=True)
    trouble_time_AE_game_core = db.Column(db.Integer, index=True)
    trouble_time_AE_all_core = db.Column(db.Integer, index=True)

    trouble_time_HT_login_core = db.Column(db.Integer, index=True)
    trouble_time_HT_store_core = db.Column(db.Integer, index=True)
    trouble_time_HT_register_core = db.Column(db.Integer, index=True)
    trouble_time_HT_game_core = db.Column(db.Integer, index=True)
    trouble_time_HT_all_core = db.Column(db.Integer, index=True)

    trouble_time_KR_login_core = db.Column(db.Integer, index=True)
    trouble_time_KR_store_core = db.Column(db.Integer, index=True)
    trouble_time_KR_register_core = db.Column(db.Integer, index=True)
    trouble_time_KR_game_core = db.Column(db.Integer, index=True)
    trouble_time_KR_all_core = db.Column(db.Integer, index=True)

    trouble_time_CN_login_core = db.Column(db.Integer, index=True)
    trouble_time_CN_store_core = db.Column(db.Integer, index=True)
    trouble_time_CN_register_core = db.Column(db.Integer, index=True)
    trouble_time_CN_game_core = db.Column(db.Integer, index=True)
    trouble_time_CN_all_core = db.Column(db.Integer, index=True)

    trouble_time_GB_login_core = db.Column(db.Integer, index=True)
    trouble_time_GB_store_core = db.Column(db.Integer, index=True)
    trouble_time_GB_register_core = db.Column(db.Integer, index=True)
    trouble_time_GB_game_core = db.Column(db.Integer, index=True)
    trouble_time_GB_all_core = db.Column(db.Integer, index=True)

    trouble_time_ALL_login_core = db.Column(db.Integer, index=True)
    trouble_time_ALL_store_core = db.Column(db.Integer, index=True)
    trouble_time_ALL_register_core = db.Column(db.Integer, index=True)
    trouble_time_ALL_game_core = db.Column(db.Integer, index=True)
    trouble_time_ALL_all_core = db.Column(db.Integer, index=True)

    trouble_time_AE_active = db.Column(db.Integer, index=True)
    trouble_time_AE_platform = db.Column(db.Integer, index=True)
    trouble_time_AE_backstage = db.Column(db.Integer, index=True)
    trouble_time_AE_other = db.Column(db.Integer, index=True)

    trouble_time_HT_active = db.Column(db.Integer, index=True)
    trouble_time_HT_platform = db.Column(db.Integer, index=True)
    trouble_time_HT_backstage = db.Column(db.Integer, index=True)
    trouble_time_HT_other = db.Column(db.Integer, index=True)

    trouble_time_KR_active = db.Column(db.Integer, index=True)
    trouble_time_KR_platform = db.Column(db.Integer, index=True)
    trouble_time_KR_backstage = db.Column(db.Integer, index=True)
    trouble_time_KR_other = db.Column(db.Integer, index=True)

    trouble_time_CN_active = db.Column(db.Integer, index=True)
    trouble_time_CN_platform = db.Column(db.Integer, index=True)
    trouble_time_CN_backstage = db.Column(db.Integer, index=True)
    trouble_time_CN_other = db.Column(db.Integer, index=True)

    trouble_time_GB_active = db.Column(db.Integer, index=True)
    trouble_time_GB_platform = db.Column(db.Integer, index=True)
    trouble_time_GB_backstage = db.Column(db.Integer, index=True)
    trouble_time_GB_other = db.Column(db.Integer, index=True)

    trouble_time_is_core = db.Column(db.Integer, index=True)
    trouble_time_not_core = db.Column(db.Integer, index=True)

    def __repr__(self):
        return 'trouble_month %r' % self.trouble_month

class Anomaly_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anomaly_affair = db.Column(db.String(128), index=True)
    oper_center = db.Column(db.String(32), index=True)
    anomaly_source = db.Column(db.String(32), index=True)
    anomaly_type = db.Column(db.String(32), index=True)
    business_module = db.Column(db.String(64), index=True)
    anomaly_level = db.Column(db.String(32), index=True)
    isnot_fake = db.Column(db.String(32), index=True)
    isnot_maintain = db.Column(db.String(32), index=True)
    isnot_affect = db.Column(db.String(32), index=True)
    occurrence_time = db.Column(db.String(32), index=True)
    error_time = db.Column(db.String(32), index=True)
    processing_stime = db.Column(db.String(32), index=True)
    processing_etime = db.Column(db.String(32), index=True)
    processing_ltime = db.Column(db.String(32), index=True)
    anomaly_attr = db.Column(db.String(64), index=True)
    processor = db.Column(db.String(64), index=True)
    result = db.Column(db.String(64), index=True)
    five_minutes = db.Column(db.String(256), index=True)
    fifteen_minutes = db.Column(db.String(256), index=True)
    thirty_minutes = db.Column(db.String(256), index=True)
    an_hour = db.Column(db.String(256), index=True)
    two_hours = db.Column(db.String(256), index=True)
    evaluation = db.Column(db.String(32), index=True)
    monitor_follow_people = db.Column(db.String(32), index=True)

    def __repr__(self):
        return '%r' % self.id


class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    main_id = db.Column(db.String(32), index=True)
    group_name = db.Column(db.String(64), index=True)
    main_type = db.Column(db.String(32), index=True)
    start_time = db.Column(db.String(32), index=True)
    end_time = db.Column(db.String(32), index=True)
    main_info = db.Column(db.String(256), index=True)
    def __repr__(self):
        return '%r' % self.id

class Zabbix_group(db.Model):
    group_id = db.Column(db.Integer,primary_key=True)
    group_name = db.Column(db.String(128), index=True)
    def __repr__(self):
        return '%r' % self.group_id



#审批使用的临时数据库结构
class Approve_Tmp(db.Model):

    __tablename__='approve_tmp'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, unique=False)               #更新该功能用户信息
    flush_date = db.Column(db.DateTime, default=datetime)       #更新日期，可缺省
    db_name = db.Column(db.String(64), unique=False)            #更新数据库名称
    db_id = db.Column(db.Integer, unique=False)                 #更新id

    def __repr__(self):
        return "<Approve_Tmp:%s>" %self.id







