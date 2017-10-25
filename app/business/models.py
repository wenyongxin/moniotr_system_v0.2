#!/usr/bin/env python
#ecoding:utf-8

from .. import db


class Manager_business(db.Model):

    __tablename__ = 'manager_business'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    describe = db.Column(db.String(64), nullable=False)
    sort = db.Column(db.String(10), nullable=False)
    sections_id = db.Column(db.Integer, db.ForeignKey('sections.id'))
    sections = db.relationship('Sections')
    items = db.Column(db.String(512), nullable=False)
    hostip = db.Column(db.String(20), nullable=False)


    def __repr__(self):
        return '<Manager_business:%s>' %self.id

#存储历史记录数据（数据类型整数、浮点数等）
class History_Number(db.Model):

    __tablename__='history_Number'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    itemid = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    # value = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float, nullable=False)


    def __repr__(self):
        return '<History_Number:%s>' %self.id


#存储历史记录输入（数据类型字符串，一般用于存储异常错误信息）
class History_String(db.Model):

    __tablename__='history_string'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    itemid = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<History_String:%s>' %self.id
