#!/usr/bin/env python
#ecoding:utf-8

from .. import db


class Game_Ascritption(db.Model):

    __tablename__='game_ascription'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    center_name = db.Column(db.Integer, nullable=False)                 #运营中心名称id
    game_name = db.Column(db.Integer, nullable=False, unique=True)      #游戏名称id
    game_one = db.Column(db.String(64), nullable=False)                 #第一负责人名称
    game_two = db.Column(db.String(64), nullable=False)                 #第二负责人名称
    game_factory = db.Column(db.String(64), nullable=False)             #原厂名称
    game_autonomy = db.Column(db.Boolean, default=False)                #是否自主运维
    game_online = db.Column(db.Boolean, default=False)                  #是否上线
    game_operate = db.Column(db.String(64), nullable=False)             #运营负责人名称
    game_approve = db.Column(db.Boolean, default=False)                 #是否审批通过

    def __repr__(self):
        return '<Game_Ascritption:%s>' %self.id


class Game_auth(db.Model):

    __tablename__='game_auth'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    auth = db.Column(db.String(128), nullable=False, unique=True)

    def __repr__(self):
        return '<Game_auth:%s>' %self.id



