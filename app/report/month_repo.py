#coding: utf-8

import time,datetime,json,re,calendar,sys

from . import report
from .. import db, csrf
from flask_login import login_required
from .. decorators import user_required
from flask import render_template, flash, redirect, session, url_for, request,Response
from .. models import Sections, Permission_Model, Permission
from .. models import User,Trouble_repo,Trouble_repo_add,Month_trouble_repo,Month_trouble_log,Anomaly_log
import export_excel

sys.path.append('../..')
import config


@report.route('/monthrepo/', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
def month_repo():
    # 内外故障参数定义
    trouble_time_yw_inner = 0
    trouble_time_ywkf_inner = 0
    trouble_time_jckf_inner = 0
    trouble_time_all = 0

    trouble_time_inner = 0
    trouble_time_out = 0

    #各部门部门故障参数定义
    trouble_time_yw = 0
    trouble_time_ywkf = 0
    trouble_time_jckf = 0
    trouble_time_dsf = 0

    trouble_time_core = 0
    trouble_time_ncore = 0

    trouble_time_yw_core = 0
    trouble_time_yw_ncore = 0

    trouble_time_ywkf_core = 0
    trouble_time_ywkf_ncore = 0

    trouble_time_jckf_core = 0
    trouble_time_jckf_ncore = 0

    trouble_time_dsf_core = 0
    trouble_time_dsf_ncore = 0

    #故障类型参数定义
    trouble_time_server = 0
    trouble_time_perple = 0
    trouble_time_bug = 0
    trouble_time_safe = 0
    trouble_time_dsf_t = 0
    trouble_time_once = 0
    trouble_time_net = 0


    #用户体验数据一级指标参数定义
    trouble_time_AE_login = 0
    trouble_time_AE_store = 0
    trouble_time_AE_register = 0
    trouble_time_AE_game = 0
    trouble_time_AE_all = 0
    AE_row = 4

    trouble_time_HT_login = 0
    trouble_time_HT_store = 0
    trouble_time_HT_register = 0
    trouble_time_HT_game = 0
    trouble_time_HT_all = 0
    HT_row = 4

    trouble_time_KR_login = 0
    trouble_time_KR_store = 0
    trouble_time_KR_register = 0
    trouble_time_KR_game = 0
    trouble_time_KR_all = 0
    KR_row = 4

    trouble_time_CN_login = 0
    trouble_time_CN_store = 0
    trouble_time_CN_register = 0
    trouble_time_CN_game = 0
    trouble_time_CN_all = 0
    CN_row = 4

    trouble_time_GB_login = 0
    trouble_time_GB_store = 0
    trouble_time_GB_register = 0
    trouble_time_GB_game = 0
    trouble_time_GB_all= 0
    GB_row = 4

    trouble_time_ALL_login = 0
    trouble_time_ALL_store = 0
    trouble_time_ALL_register = 0
    trouble_time_ALL_game = 0
    trouble_time_ALL_all = 0
    ALL_row = 0
    ALL_row_pk = 0




    #用户体验数据二级指标参数定义
    trouble_time_AE_active = 0
    trouble_time_AE_platform = 0
    trouble_time_AE_backstage = 0
    trouble_time_AE_other = 0

    trouble_time_HT_active = 0
    trouble_time_HT_platform = 0
    trouble_time_HT_backstage = 0
    trouble_time_HT_other = 0

    trouble_time_KR_active = 0
    trouble_time_KR_platform = 0
    trouble_time_KR_backstage = 0
    trouble_time_KR_other = 0

    trouble_time_CN_active = 0
    trouble_time_CN_platform = 0
    trouble_time_CN_backstage = 0
    trouble_time_CN_other = 0

    trouble_time_GB_active = 0
    trouble_time_GB_platform = 0
    trouble_time_GB_backstage = 0
    trouble_time_GB_other = 0

    trouble_time_is_core = 0
    trouble_time_not_core = 0

    trouble_time_yy = 0
    trouble_time_yy_core = 0
    trouble_time_yy_ncore = 0

    one_row = 21
    one_row_pk = 21

    #获取要查看故障分析的月份
    #this_month = '2017-01'


    change_month = request.form.get('month',None)
    if change_month:
        this_month = change_month
        today = "%s-01" % this_month
        today = datetime.datetime.strptime(today, "%Y-%m-%d").date()

    else:
        today = datetime.date.today()

        this_month = today.strftime('%Y-%m')

    #获取上个月日期
    #last_month_date = '2016-12'
    last_month_date = (today.replace(day=1) - datetime.timedelta(1)).replace(day=1).strftime('%Y-%m')

    #获取当月详细故障信息
    trouble_infos = Trouble_repo.query.filter(Trouble_repo.trouble_date.ilike("%s%%" % this_month),Trouble_repo.trouble_status==u'完成').order_by(Trouble_repo.trouble_date)

    #清空当月摘要故障信息信息
    del_infos = Month_trouble_repo.query.all()
    for  i in del_infos:
        db.session.delete(i)
    db.session.commit()


    #添加当月摘要故障信息
    for i in trouble_infos:
        trouble_date = i.trouble_date
        operating_center = i.operating_center
        business_module =  i.business_module
        isnot_inner = i.isnot_inner
        affect_time = i.affect_time
        isnot_experience = i.isnot_experience
        isnot_core = i.isnot_core
        trouble_type = i.trouble_type
        trouble_attr = i.trouble_attr
        trouble_status = i.trouble_status
        if trouble_status == u'完成':
            info = Month_trouble_repo(trouble_date=trouble_date,operating_center=operating_center,business_module=business_module,
                     isnot_inner=isnot_inner,affect_time=affect_time,isnot_experience=isnot_experience,
                     isnot_core=isnot_core,trouble_type=trouble_type,trouble_attr=trouble_attr)
            db.session.add(info)
    db.session.commit()


    #获取当月摘要故障信息
    troubles = Month_trouble_repo.query.all()

    #获取上个月的用户体验指标数据
    last_month = Month_trouble_log.query.filter_by(trouble_month=last_month_date).first()

    try:

        last_month_trouble_time = int(last_month.trouble_time_not_core)+int(last_month.trouble_time_is_core)
    except:
        last_month_trouble_time = 0


    #计算当月的时间（分钟）
    days = int(calendar.monthrange(int(this_month.split('-')[0]),int(this_month.split('-')[1]))[1])
    month_time = 60*24*days


    for i in troubles:
        trouble_attr = i.trouble_attr
        trouble_type = i.trouble_type
        isnot_inner = i.isnot_inner
        isnot_core = i.isnot_core
        isnot_experience = i.isnot_experience
        operating_center = i.operating_center
        business_module = i.business_module
        try:
            affect_time = int(i.affect_time)
        except:
            affect_time = 0
        trouble_time_all += affect_time




        #用户体验指标数据
        if isnot_core == u'是':
            trouble_time_is_core += affect_time
            if operating_center == u'亚欧':
                if business_module == u'登陆':
                    trouble_time_AE_login += affect_time
                elif business_module == u'储值':
                    trouble_time_AE_store += affect_time
                elif business_module == u'注册':
                    trouble_time_AE_register += affect_time
                elif re.search(r'-',business_module):
                    trouble_time_AE_game += affect_time
                elif re.search(r'ALL',business_module):
                    trouble_time_AE_all += affect_time
                else:
                    trouble_time_AE_game += affect_time


            elif operating_center == u'港台':
                if business_module == u'登陆':
                    trouble_time_HT_login += affect_time
                elif business_module == u'储值':
                    trouble_time_HT_store += affect_time
                elif business_module == u'注册':
                    trouble_time_HT_register += affect_time
                elif re.search(r'-', business_module):
                    trouble_time_HT_game += affect_time
                elif re.search(r'ALL', business_module):
                    trouble_time_HT_all += affect_time
                else:
                    trouble_time_HT_game += affect_time


            elif operating_center == u'韩国':
                if business_module == u'登陆':
                    trouble_time_KR_login += affect_time
                elif business_module == u'储值':
                    trouble_time_KR_store += affect_time
                elif business_module == u'注册':
                    trouble_time_KR_register += affect_time
                elif re.search(r'-', business_module):
                    trouble_time_KR_game += affect_time
                elif re.search(r'ALL', business_module):
                    trouble_time_KR_all += affect_time
                    one_row +=1
                    KR_row += 1
                else:
                    trouble_time_KR_game += affect_time


            elif operating_center == u'国内':
                if business_module == u'登陆':
                    trouble_time_CN_login += affect_time
                elif business_module == u'储值':
                    trouble_time_CN_store += affect_time
                elif business_module == u'注册':
                    trouble_time_CN_register += affect_time
                elif re.search(r'-', business_module):
                    trouble_time_CN_game += affect_time
                elif re.search(r'ALL', business_module):
                    trouble_time_CN_all += affect_time
                    one_row +=1
                    CN_row += 1
                else:
                    trouble_time_CN_game += affect_time

            elif operating_center == u'全球':
                if business_module == u'登陆':
                    trouble_time_GB_login += affect_time
                elif business_module == u'储值':
                    trouble_time_GB_store += affect_time
                elif business_module == u'注册':
                    trouble_time_GB_register += affect_time
                elif re.search(r'-', business_module):
                    trouble_time_GB_game += affect_time
                elif re.search(r'ALL', business_module):
                    trouble_time_GB_all += affect_time
                else:
                    trouble_time_GB_game += affect_time


            elif operating_center == u'ALL':
                if business_module == u'登陆':
                    trouble_time_ALL_login += affect_time

                elif business_module == u'储值':
                    trouble_time_ALL_store += affect_time

                elif business_module == u'注册':
                    trouble_time_ALL_register += affect_time

                elif re.search(r'-', business_module):
                    trouble_time_ALL_game += affect_time

                elif re.search(r'ALL', business_module):
                    trouble_time_ALL_all += affect_time
                else:
                    trouble_time_ALL_game += affect_time

        #各运营中心二级指标数据统计
        else:
            trouble_time_not_core += affect_time
            if operating_center == u'亚欧':
                if business_module == u'活动':
                    trouble_time_AE_active += affect_time
                elif business_module == u'平台':
                    trouble_time_AE_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_AE_backstage += affect_time
                else:
                    trouble_time_AE_other += affect_time

            elif operating_center == u'港台':
                if business_module == u'活动':
                    trouble_time_HT_active += affect_time
                elif business_module == u'平台':
                    trouble_time_HT_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_HT_backstage += affect_time
                else:
                    trouble_time_HT_other += affect_time

            elif operating_center == u'韩国':
                if business_module == u'活动':
                    trouble_time_KR_active += affect_time
                elif business_module == u'平台':
                    trouble_time_KR_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_KR_backstage += affect_time
                else:
                    trouble_time_KR_other += affect_time

            elif operating_center == u'国内':
                if business_module == u'活动':
                    trouble_time_CN_active += affect_time
                elif business_module == u'平台':
                    trouble_time_CN_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_CN_backstage += affect_time
                else:
                    trouble_time_CN_other += affect_time

            elif operating_center == u'全球':
                if business_module == u'活动':
                    trouble_time_GB_active += affect_time
                elif business_module == u'平台':
                    trouble_time_GB_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_GB_backstage += affect_time
                else:
                    trouble_time_GB_other += affect_time
            else:
                trouble_time_OT += affect_time



        #各部门故障
        if trouble_attr == u'运维':
            trouble_time_yw += affect_time
            if isnot_core == u'是':
                 trouble_time_yw_core += affect_time
            else:
                 trouble_time_yw_ncore += affect_time

        elif trouble_attr == u'业务开发':
            trouble_time_ywkf += affect_time
            if isnot_core == u'是':
                 trouble_time_ywkf_core += affect_time
            else:
                 trouble_time_ywkf_ncore += affect_time

        elif trouble_attr == u'基础开发':
            trouble_time_jckf += affect_time
            if isnot_core == u'是':
                 trouble_time_jckf_core += affect_time
            else:
                 trouble_time_jckf_ncore += affect_time

        elif re.search(u'运营',trouble_attr):
            trouble_time_yy += affect_time
            if isnot_core == u'是':
                trouble_time_yy_core += affect_time
            else:
                trouble_time_yy_ncore += affect_time

        elif re.search(u'第三方',trouble_attr):
            trouble_time_dsf += affect_time
            if isnot_core == u'是':
                 trouble_time_dsf_core += affect_time
            else:
                 trouble_time_dsf_ncore += affect_time

        else:
            print u"有其他的归属,请检查! %s" % (trouble_attr)



        #内外部故障
        if isnot_inner == u'是':
            trouble_time_inner += affect_time
            if trouble_attr == u'运维':
                trouble_time_yw_inner += affect_time
            elif trouble_attr == u'业务开发':
                trouble_time_ywkf_inner += affect_time
            elif trouble_attr == u'基础开发':
                trouble_time_jckf_inner += affect_time

        elif isnot_inner == u'否':
            trouble_time_out += affect_time


        if isnot_core == u'是':
            trouble_time_core += affect_time
        else:
            trouble_time_ncore += affect_time



       #故障类型

        if  trouble_type == u'服务器故障':
            trouble_time_server += affect_time
        elif  trouble_type == u'人为故障':
            trouble_time_perple += affect_time
        elif  trouble_type == u'BUG类型故障':
            trouble_time_bug += affect_time
        elif  trouble_type == u'安全类型故障':
            trouble_time_safe += affect_time
        elif  trouble_type == u'第三方故障':
            trouble_time_dsf_t += affect_time
        elif  trouble_type == u'网络故障':
            trouble_time_net += affect_time
        elif trouble_type == u'偶然性故障':
            trouble_time_once += affect_time


    #####################################
    if trouble_time_ALL_login >0:
        one_row += 1
        ALL_row += 1
    if trouble_time_ALL_store>0:
        one_row += 1
        ALL_row += 1
    if trouble_time_ALL_register>0:
        one_row += 1
        ALL_row += 1
    if trouble_time_ALL_game>0:
        one_row += 1
        ALL_row += 1
    if trouble_time_ALL_all>0:
        one_row += 1
        ALL_row += 1
    #####################################

    if trouble_time_AE_all > 0:
        one_row += 1
        AE_row += 1

    if trouble_time_HT_all > 0:
        one_row += 1
        HT_row += 1

    if trouble_time_KR_all > 0:
        one_row += 1
        KR_row += 1

    if trouble_time_CN_all > 0:
        one_row += 1
        CN_row += 1

    if trouble_time_GB_all > 0:
        one_row += 1
        GB_row += 1


    #####################################
    if trouble_time_AE_all > 0 or last_month.trouble_time_AE_all_core > 0:
        one_row_pk += 1
    if trouble_time_HT_all > 0 or last_month.trouble_time_HT_all_core > 0:
        one_row_pk += 1
    if trouble_time_KR_all > 0 or last_month.trouble_time_KR_all_core > 0:
        one_row_pk += 1
    if trouble_time_CN_all > 0 or last_month.trouble_time_CN_all_core > 0:
        one_row_pk += 1
    if trouble_time_GB_all > 0 or last_month.trouble_time_GB_all_core > 0:
        one_row_pk += 1

    #####################################

    if trouble_time_ALL_login >0 or last_month.trouble_time_ALL_login_core >0:
        ALL_row_pk += 1
        one_row_pk += 1
    if trouble_time_ALL_store > 0 or last_month.trouble_time_ALL_store_core > 0:
        ALL_row_pk += 1
        one_row_pk += 1
    if trouble_time_ALL_register > 0 or last_month.trouble_time_ALL_register_core > 0:
        ALL_row_pk += 1
        one_row_pk += 1
    if trouble_time_ALL_game > 0 or last_month.trouble_time_ALL_game_core > 0:
        ALL_row_pk += 1
        one_row_pk += 1
    if trouble_time_ALL_all > 0 or last_month.trouble_time_ALL_all_core > 0:
        ALL_row_pk += 1
        one_row_pk += 1

    if ALL_row >0:
        one_row +=1
    if ALL_row >0 or ALL_row_pk>0:
        one_row_pk +=1
    ##############记录每个月的各项业务模块用户体验数据###############

    if trouble_time_all == 0:
        trouble_time_all = 1
    else:
        pass

    #删除旧数据
    try:
        this_month_del = Month_trouble_log.query.filter_by(trouble_month=this_month).first()
        db.session.delete(this_month_del)
        db.session.commit()
    except:
        pass
    #记录新数据
    try:
        info = Month_trouble_log(
            trouble_month=this_month,
            trouble_time_AE_login_core=trouble_time_AE_login,
            trouble_time_AE_store_core=trouble_time_AE_store,
            trouble_time_AE_register_core=trouble_time_AE_register,
            trouble_time_AE_game_core=trouble_time_AE_game,
            trouble_time_AE_all_core=trouble_time_AE_all,

            trouble_time_HT_login_core=trouble_time_HT_login,
            trouble_time_HT_store_core=trouble_time_HT_store,
            trouble_time_HT_register_core=trouble_time_HT_register,
            trouble_time_HT_game_core=trouble_time_HT_game,
            trouble_time_HT_all_core=trouble_time_HT_all,


            trouble_time_KR_login_core=trouble_time_KR_login,
            trouble_time_KR_store_core=trouble_time_KR_store,
            trouble_time_KR_register_core=trouble_time_KR_register,
            trouble_time_KR_game_core=trouble_time_KR_game,
            trouble_time_KR_all_core=trouble_time_KR_all,


            trouble_time_CN_login_core=trouble_time_CN_login,
            trouble_time_CN_store_core=trouble_time_CN_store,
            trouble_time_CN_register_core=trouble_time_CN_register,
            trouble_time_CN_game_core=trouble_time_CN_game,
            trouble_time_CN_all_core=trouble_time_CN_all,


            trouble_time_GB_login_core=trouble_time_GB_login,
            trouble_time_GB_store_core=trouble_time_GB_store,
            trouble_time_GB_register_core=trouble_time_GB_register,
            trouble_time_GB_game_core=trouble_time_GB_game,
            trouble_time_GB_all_core=trouble_time_GB_all,

            trouble_time_ALL_login_core=trouble_time_ALL_login,
            trouble_time_ALL_store_core=trouble_time_ALL_store,
            trouble_time_ALL_register_core=trouble_time_ALL_register,
            trouble_time_ALL_game_core=trouble_time_ALL_game,
            trouble_time_ALL_all_core=trouble_time_ALL_all,


            trouble_time_AE_active = trouble_time_AE_active,
            trouble_time_AE_platform = trouble_time_AE_platform,
            trouble_time_AE_backstage = trouble_time_AE_backstage,
            trouble_time_AE_other = trouble_time_AE_other,


            trouble_time_HT_active = trouble_time_HT_active,
            trouble_time_HT_platform = trouble_time_HT_platform,
            trouble_time_HT_backstage = trouble_time_HT_backstage,
            trouble_time_HT_other = trouble_time_HT_other,

            trouble_time_KR_active = trouble_time_KR_active,
            trouble_time_KR_platform = trouble_time_KR_platform,
            trouble_time_KR_backstage = trouble_time_KR_backstage,
            trouble_time_KR_other = trouble_time_KR_other,

            trouble_time_CN_active = trouble_time_CN_active,
            trouble_time_CN_platform = trouble_time_CN_platform,
            trouble_time_CN_backstage = trouble_time_CN_backstage,
            trouble_time_CN_other = trouble_time_CN_other,

            trouble_time_GB_active = trouble_time_GB_active,
            trouble_time_GB_platform = trouble_time_GB_platform,
            trouble_time_GB_backstage = trouble_time_GB_backstage,
            trouble_time_GB_other = trouble_time_GB_other,

            trouble_time_is_core=trouble_time_is_core,
            trouble_time_not_core=trouble_time_not_core



        )


        db.session.add(info)
        db.session.commit()
    except:
        db.session.rollback()




    ##########################二级指标展示判断############################
    rowspan_AE = 0
    rowspan_AE_1 = 0
    list_AE = []


    if trouble_time_AE_active > 0 or last_month.trouble_time_AE_active >0:
        rowspan_AE +=1
        dic_AE = [u'活动',trouble_time_AE_active,last_month.trouble_time_AE_active]
        list_AE.append(dic_AE)
    if trouble_time_AE_active > 0:
        rowspan_AE_1 += 1


    if trouble_time_AE_platform > 0 or last_month.trouble_time_AE_platform >0:
        rowspan_AE += 1
        dic_AE = [u'平台', trouble_time_AE_platform,last_month.trouble_time_AE_platform]
        list_AE.append(dic_AE)
    if trouble_time_AE_platform > 0 :
        rowspan_AE_1 += 1


    if trouble_time_AE_backstage > 0 or last_month.trouble_time_AE_backstage>0:
        rowspan_AE += 1
        dic_AE = [u'后台', trouble_time_AE_backstage,last_month.trouble_time_AE_backstage]
        list_AE.append(dic_AE)
    if trouble_time_AE_backstage > 0:
        rowspan_AE_1 += 1

    if trouble_time_AE_other > 0 or last_month.trouble_time_AE_other>0:
        rowspan_AE += 1
        dic_AE = [u'其他',trouble_time_AE_other,last_month.trouble_time_AE_other]
        list_AE.append(dic_AE)
    if trouble_time_AE_other > 0 :
        rowspan_AE_1 += 1


    ##########################二级指标展示判断############################
    rowspan_HT = 0
    rowspan_HT_1 = 0
    list_HT = []


    if trouble_time_HT_active > 0 or last_month.trouble_time_HT_active>0:
        rowspan_HT +=1
        dic_AE = [u'活动', trouble_time_HT_active,last_month.trouble_time_HT_active]
        list_HT.append(dic_AE)
    if trouble_time_HT_active > 0 :
        rowspan_HT_1 += 1

    if trouble_time_HT_platform > 0 or last_month.trouble_time_HT_platform>0:
        rowspan_HT += 1
        dic_AE = [u'平台', trouble_time_HT_platform,last_month.trouble_time_HT_platform]
        list_HT.append(dic_AE)
    if trouble_time_HT_platform > 0 :
        rowspan_HT_1 += 1

    if trouble_time_HT_backstage > 0 or last_month.trouble_time_HT_backstage>0:
        rowspan_HT += 1
        dic_AE = [u'后台', trouble_time_HT_backstage,last_month.trouble_time_HT_backstage]
        list_HT.append(dic_AE)
    if trouble_time_HT_backstage > 0 :
        rowspan_HT_1 += 1

    if trouble_time_HT_other > 0 or last_month.trouble_time_HT_other>0:
        rowspan_HT += 1
        dic_AE = [u'其他', trouble_time_HT_other,last_month.trouble_time_HT_other]
        list_HT.append(dic_AE)
    if trouble_time_HT_other > 0 :
        rowspan_HT_1 += 1

        ##########################二级指标展示判断############################
    rowspan_KR = 0
    rowspan_KR_1 = 0
    list_KR = []


    if trouble_time_KR_active > 0 or last_month.trouble_time_KR_active>0:
        rowspan_KR +=1
        dic_AE = [u'活动', trouble_time_KR_active,last_month.trouble_time_KR_active]
        list_KR.append(dic_AE)
    if trouble_time_KR_active > 0 :
        rowspan_KR_1 += 1

    if trouble_time_KR_platform > 0 or last_month.trouble_time_KR_platform>0:
        rowspan_KR += 1
        dic_AE = [u'平台', trouble_time_KR_platform,last_month.trouble_time_KR_platform]
        list_KR.append(dic_AE)
    if trouble_time_KR_platform > 0 :
        rowspan_KR_1 += 1

    if trouble_time_KR_backstage > 0 or last_month.trouble_time_KR_backstage>0:
        rowspan_KR += 1
        dic_AE = [u'后台', trouble_time_KR_backstage,last_month.trouble_time_KR_backstage]
        list_KR.append(dic_AE)
    if trouble_time_KR_backstage > 0 :
        rowspan_KR_1 += 1

    if trouble_time_KR_other > 0 or last_month.trouble_time_KR_other>0:
        rowspan_KR += 1
        dic_AE = [u'其他', trouble_time_KR_other,last_month.trouble_time_KR_other]
        list_KR.append(dic_AE)
    if trouble_time_KR_other > 0:
        rowspan_KR_1 += 1

        ##########################二级指标展示判断############################
    rowspan_CN = 0
    rowspan_CN_1 = 0
    list_CN = []


    if trouble_time_CN_active > 0 or last_month.trouble_time_CN_active>0:
        rowspan_CN +=1
        dic_AE = [u'活动', trouble_time_CN_active,last_month.trouble_time_CN_active]
        list_CN.append(dic_AE)
    if trouble_time_CN_active > 0 :
        rowspan_CN_1 += 1

    if trouble_time_CN_platform > 0 or last_month.trouble_time_CN_platform>0:
        rowspan_CN += 1
        dic_AE = [u'平台', trouble_time_CN_platform,last_month.trouble_time_CN_platform]
        list_CN.append(dic_AE)
    if trouble_time_CN_platform > 0 :
        rowspan_CN_1 += 1

    if trouble_time_CN_backstage > 0 or last_month.trouble_time_CN_backstage>0:
        rowspan_CN += 1
        dic_AE = [u'后台', trouble_time_CN_backstage,last_month.trouble_time_CN_backstage]
        list_CN.append(dic_AE)
    if trouble_time_CN_backstage > 0 :
        rowspan_CN_1 += 1

    if trouble_time_CN_other > 0 or last_month.trouble_time_CN_other>0:
        rowspan_CN += 1
        dic_AE = [u'其他', trouble_time_CN_other,last_month.trouble_time_CN_other]
        list_CN.append(dic_AE)
    if trouble_time_CN_other > 0 :
        rowspan_CN_1 += 1


        ##########################二级指标展示判断############################
    rowspan_GB = 0
    rowspan_GB_1 = 0
    list_GB = []


    if trouble_time_GB_active > 0 or last_month.trouble_time_GB_active>0:
        rowspan_GB +=1
        dic_AE = [u'活动', trouble_time_GB_active,last_month.trouble_time_GB_active]
        list_GB.append(dic_AE)
    if trouble_time_GB_active > 0 :
        rowspan_GB_1 += 1

    if trouble_time_GB_platform > 0 or last_month.trouble_time_GB_platform>0:
        rowspan_GB += 1
        dic_AE = [u'平台', trouble_time_GB_platform,last_month.trouble_time_GB_platform]
        list_GB.append(dic_AE)
    if trouble_time_GB_platform > 0 :
        rowspan_GB_1 += 1

    if trouble_time_GB_backstage > 0 or last_month.trouble_time_GB_backstage>0:
        rowspan_GB += 1
        dic_AE = [u'后台', trouble_time_GB_backstage,last_month.trouble_time_GB_backstage]
        list_GB.append(dic_AE)
    if trouble_time_GB_backstage > 0:
        rowspan_GB_1 += 1

    if trouble_time_GB_other > 0 or last_month.trouble_time_GB_other>0:
        rowspan_GB += 1
        dic_AE = [u'其他', trouble_time_GB_other,last_month.trouble_time_GB_other]
        list_GB.append(dic_AE)
    if trouble_time_GB_other > 0:
        rowspan_GB_1 += 1

    if change_month:
        return render_template('report/month_repo_body.html', **locals())
    else:
        return render_template('report/month_repo.html',**locals())


@report.route('/exportmonth/', methods=['POST','GET'])
@user_required
@login_required
@csrf.exempt
def month_export():
    # 内外故障参数定义
    trouble_time_yw_inner = 0
    trouble_time_ywkf_inner = 0
    trouble_time_jckf_inner = 0
    trouble_time_all = 0

    trouble_time_inner = 0
    trouble_time_out = 0

    #各部门部门故障参数定义
    trouble_time_yw = 0
    trouble_time_ywkf = 0
    trouble_time_jckf = 0
    trouble_time_dsf = 0

    trouble_time_core = 0
    trouble_time_ncore = 0

    trouble_time_yw_core = 0
    trouble_time_yw_ncore = 0

    trouble_time_ywkf_core = 0
    trouble_time_ywkf_ncore = 0

    trouble_time_jckf_core = 0
    trouble_time_jckf_ncore = 0

    trouble_time_dsf_core = 0
    trouble_time_dsf_ncore = 0

    #故障类型参数定义
    trouble_time_server = 0
    trouble_time_perple = 0
    trouble_time_bug = 0
    trouble_time_safe = 0
    trouble_time_dsf_t = 0
    trouble_time_once = 0
    trouble_time_net = 0


    #用户体验数据一级指标参数定义
    trouble_time_AE_login = 0
    trouble_time_AE_store = 0
    trouble_time_AE_register = 0
    trouble_time_AE_game = 0
    trouble_time_AE_all = 0
    AE_row = 4

    trouble_time_HT_login = 0
    trouble_time_HT_store = 0
    trouble_time_HT_register = 0
    trouble_time_HT_game = 0
    trouble_time_HT_all = 0
    HT_row = 4

    trouble_time_KR_login = 0
    trouble_time_KR_store = 0
    trouble_time_KR_register = 0
    trouble_time_KR_game = 0
    trouble_time_KR_all = 0
    KR_row = 4

    trouble_time_CN_login = 0
    trouble_time_CN_store = 0
    trouble_time_CN_register = 0
    trouble_time_CN_game = 0
    trouble_time_CN_all = 0
    CN_row = 4

    trouble_time_GB_login = 0
    trouble_time_GB_store = 0
    trouble_time_GB_register = 0
    trouble_time_GB_game = 0
    trouble_time_GB_all= 0
    GB_row = 4

    trouble_time_ALL_login = 0
    trouble_time_ALL_store = 0
    trouble_time_ALL_register = 0
    trouble_time_ALL_game = 0
    trouble_time_ALL_all = 0
    ALL_row = 0
    ALL_row_pk = 0


    #用户体验数据二级指标参数定义
    trouble_time_AE_active = 0
    trouble_time_AE_platform = 0
    trouble_time_AE_backstage = 0
    trouble_time_AE_other = 0

    trouble_time_HT_active = 0
    trouble_time_HT_platform = 0
    trouble_time_HT_backstage = 0
    trouble_time_HT_other = 0

    trouble_time_KR_active = 0
    trouble_time_KR_platform = 0
    trouble_time_KR_backstage = 0
    trouble_time_KR_other = 0

    trouble_time_CN_active = 0
    trouble_time_CN_platform = 0
    trouble_time_CN_backstage = 0
    trouble_time_CN_other = 0

    trouble_time_GB_active = 0
    trouble_time_GB_platform = 0
    trouble_time_GB_backstage = 0
    trouble_time_GB_other = 0

    trouble_time_is_core = 0
    trouble_time_not_core = 0

    trouble_time_yy = 0
    trouble_time_yy_core = 0
    trouble_time_yy_ncore = 0

    one_row = 21
    one_row_pk = 21

    #获取要查看故障分析的月份
    #this_month = '2017-01'

    change_month = request.form.get('month',None)
    if change_month:
        this_month = change_month
        today = "%s-01" % this_month
        today = datetime.datetime.strptime(today, "%Y-%m-%d").date()

    else:
        today = datetime.date.today()

        this_month = today.strftime('%Y-%m')

    #获取上个月日期
    #last_month_date = '2016-12'
    last_month_date = (today.replace(day=1) - datetime.timedelta(1)).replace(day=1).strftime('%Y-%m')

    #获取当月详细故障信息
    trouble_infos = Trouble_repo.query.filter(Trouble_repo.trouble_date.ilike("%s%%" % this_month),Trouble_repo.trouble_status==u'完成').order_by(Trouble_repo.trouble_date)

    #清空当月摘要故障信息信息
    del_infos = Month_trouble_repo.query.all()
    for  i in del_infos:
        db.session.delete(i)
    db.session.commit()


    #添加当月摘要故障信息
    for i in trouble_infos:
        trouble_date = i.trouble_date
        operating_center = i.operating_center
        business_module =  i.business_module
        isnot_inner = i.isnot_inner
        affect_time = i.affect_time
        isnot_experience = i.isnot_experience
        isnot_core = i.isnot_core
        trouble_type = i.trouble_type
        trouble_attr = i.trouble_attr
        trouble_status = i.trouble_status
        if trouble_status == u'完成':
            info = Month_trouble_repo(trouble_date=trouble_date,operating_center=operating_center,business_module=business_module,
                     isnot_inner=isnot_inner,affect_time=affect_time,isnot_experience=isnot_experience,
                     isnot_core=isnot_core,trouble_type=trouble_type,trouble_attr=trouble_attr)
            db.session.add(info)
    db.session.commit()


    #获取当月摘要故障信息
    troubles = Month_trouble_repo.query.all()

    #获取上个月的用户体验指标数据
    last_month = Month_trouble_log.query.filter_by(trouble_month=last_month_date).first()

    try:

        last_month_trouble_time = int(last_month.trouble_time_not_core)+int(last_month.trouble_time_is_core)
    except:
        last_month_trouble_time = 0


    #计算当月的时间（分钟）
    days = int(calendar.monthrange(int(this_month.split('-')[0]),int(this_month.split('-')[1]))[1])
    month_time = 60*24*days


    for i in troubles:
        trouble_attr = i.trouble_attr
        trouble_type = i.trouble_type
        isnot_inner = i.isnot_inner
        isnot_core = i.isnot_core
        isnot_experience = i.isnot_experience
        operating_center = i.operating_center
        business_module = i.business_module
        try:
            affect_time = int(i.affect_time)
        except:
            affect_time = 0
        trouble_time_all += affect_time

        #用户体验指标数据
        if isnot_core == u'是':
            trouble_time_is_core += affect_time
            if operating_center == u'亚欧':
                if business_module == u'登陆':
                    trouble_time_AE_login += affect_time
                elif business_module == u'储值':
                    trouble_time_AE_store += affect_time
                elif business_module == u'注册':
                    trouble_time_AE_register += affect_time
                elif re.search(r'-',business_module):
                    trouble_time_AE_game += affect_time
                elif re.search(r'ALL',business_module):
                    trouble_time_AE_all += affect_time
                else:
                    trouble_time_AE_game += affect_time


            elif operating_center == u'港台':
                if business_module == u'登陆':
                    trouble_time_HT_login += affect_time
                elif business_module == u'储值':
                    trouble_time_HT_store += affect_time
                elif business_module == u'注册':
                    trouble_time_HT_register += affect_time
                elif re.search(r'-', business_module):
                    trouble_time_HT_game += affect_time
                elif re.search(r'ALL', business_module):
                    trouble_time_HT_all += affect_time
                else:
                    trouble_time_HT_game += affect_time


            elif operating_center == u'韩国':
                if business_module == u'登陆':
                    trouble_time_KR_login += affect_time
                elif business_module == u'储值':
                    trouble_time_KR_store += affect_time
                elif business_module == u'注册':
                    trouble_time_KR_register += affect_time
                elif re.search(r'-', business_module):
                    trouble_time_KR_game += affect_time
                elif re.search(r'ALL', business_module):
                    trouble_time_KR_all += affect_time
                    one_row +=1
                    KR_row += 1
                else:
                    trouble_time_KR_game += affect_time


            elif operating_center == u'国内':
                if business_module == u'登陆':
                    trouble_time_CN_login += affect_time
                elif business_module == u'储值':
                    trouble_time_CN_store += affect_time
                elif business_module == u'注册':
                    trouble_time_CN_register += affect_time
                elif re.search(r'-', business_module):
                    trouble_time_CN_game += affect_time
                elif re.search(r'ALL', business_module):
                    trouble_time_CN_all += affect_time
                    one_row +=1
                    CN_row += 1
                else:
                    trouble_time_CN_game += affect_time

            elif operating_center == u'全球':
                if business_module == u'登陆':
                    trouble_time_GB_login += affect_time
                elif business_module == u'储值':
                    trouble_time_GB_store += affect_time
                elif business_module == u'注册':
                    trouble_time_GB_register += affect_time
                elif re.search(r'-', business_module):
                    trouble_time_GB_game += affect_time
                elif re.search(r'ALL', business_module):
                    trouble_time_GB_all += affect_time
                else:
                    trouble_time_GB_game += affect_time


            elif operating_center == u'ALL':
                if business_module == u'登陆':
                    trouble_time_ALL_login += affect_time

                elif business_module == u'储值':
                    trouble_time_ALL_store += affect_time

                elif business_module == u'注册':
                    trouble_time_ALL_register += affect_time

                elif re.search(r'-', business_module):
                    trouble_time_ALL_game += affect_time

                elif re.search(r'ALL', business_module):
                    trouble_time_ALL_all += affect_time
                else:
                    trouble_time_ALL_game += affect_time

        #各运营中心二级指标数据统计
        else:
            trouble_time_not_core += affect_time
            if operating_center == u'亚欧':
                if business_module == u'活动':
                    trouble_time_AE_active += affect_time
                elif business_module == u'平台':
                    trouble_time_AE_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_AE_backstage += affect_time
                else:
                    trouble_time_AE_other += affect_time

            elif operating_center == u'港台':
                if business_module == u'活动':
                    trouble_time_HT_active += affect_time
                elif business_module == u'平台':
                    trouble_time_HT_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_HT_backstage += affect_time
                else:
                    trouble_time_HT_other += affect_time

            elif operating_center == u'韩国':
                if business_module == u'活动':
                    trouble_time_KR_active += affect_time
                elif business_module == u'平台':
                    trouble_time_KR_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_KR_backstage += affect_time
                else:
                    trouble_time_KR_other += affect_time

            elif operating_center == u'国内':
                if business_module == u'活动':
                    trouble_time_CN_active += affect_time
                elif business_module == u'平台':
                    trouble_time_CN_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_CN_backstage += affect_time
                else:
                    trouble_time_CN_other += affect_time

            elif operating_center == u'全球':
                if business_module == u'活动':
                    trouble_time_GB_active += affect_time
                elif business_module == u'平台':
                    trouble_time_GB_platform += affect_time
                elif business_module == u'后台':
                    trouble_time_GB_backstage += affect_time
                else:
                    trouble_time_GB_other += affect_time
            else:
                trouble_time_OT += affect_time



        #各部门故障
        if trouble_attr == u'运维':
            trouble_time_yw += affect_time
            if isnot_core == u'是':
                 trouble_time_yw_core += affect_time
            else:
                 trouble_time_yw_ncore += affect_time

        elif trouble_attr == u'业务开发':
            trouble_time_ywkf += affect_time
            if isnot_core == u'是':
                 trouble_time_ywkf_core += affect_time
            else:
                 trouble_time_ywkf_ncore += affect_time

        elif trouble_attr == u'基础开发':
            trouble_time_jckf += affect_time
            if isnot_core == u'是':
                 trouble_time_jckf_core += affect_time
            else:
                 trouble_time_jckf_ncore += affect_time

        elif re.search(u'运营',trouble_attr):
            trouble_time_yy += affect_time
            if isnot_core == u'是':
                trouble_time_yy_core += affect_time
            else:
                trouble_time_yy_ncore += affect_time

        elif re.search(u'第三方',trouble_attr):
            trouble_time_dsf += affect_time
            if isnot_core == u'是':
                 trouble_time_dsf_core += affect_time
            else:
                 trouble_time_dsf_ncore += affect_time

        else:
            print u"有其他的归属,请检查! %s" % (trouble_attr)



        #内外部故障
        if isnot_inner == u'是':
            trouble_time_inner += affect_time
            if trouble_attr == u'运维':
                trouble_time_yw_inner += affect_time
            elif trouble_attr == u'业务开发':
                trouble_time_ywkf_inner += affect_time
            elif trouble_attr == u'基础开发':
                trouble_time_jckf_inner += affect_time

        elif isnot_inner == u'否':
            trouble_time_out += affect_time


        if isnot_core == u'是':
            trouble_time_core += affect_time
        else:
            trouble_time_ncore += affect_time



       #故障类型

        if  trouble_type == u'服务器故障':
            trouble_time_server += affect_time
        elif  trouble_type == u'人为故障':
            trouble_time_perple += affect_time
        elif  trouble_type == u'BUG类型故障':
            trouble_time_bug += affect_time
        elif  trouble_type == u'安全类型故障':
            trouble_time_safe += affect_time
        elif  trouble_type == u'第三方故障':
            trouble_time_dsf_t += affect_time
        elif  trouble_type == u'网络故障':
            trouble_time_net += affect_time
        elif trouble_type == u'偶然性故障':
            trouble_time_once += affect_time


    #####################################
    if trouble_time_ALL_login >0:
        one_row += 1
        ALL_row += 1
    if trouble_time_ALL_store>0:
        one_row += 1
        ALL_row += 1
    if trouble_time_ALL_register>0:
        one_row += 1
        ALL_row += 1
    if trouble_time_ALL_game>0:
        one_row += 1
        ALL_row += 1
    if trouble_time_ALL_all>0:
        one_row += 1
        ALL_row += 1
    #####################################

    if trouble_time_AE_all > 0:
        one_row += 1
        AE_row += 1

    if trouble_time_HT_all > 0:
        one_row += 1
        HT_row += 1

    if trouble_time_KR_all > 0:
        one_row += 1
        KR_row += 1

    if trouble_time_CN_all > 0:
        one_row += 1
        CN_row += 1

    if trouble_time_GB_all > 0:
        one_row += 1
        GB_row += 1


    #####################################
    if trouble_time_AE_all > 0 or last_month.trouble_time_AE_all_core > 0:
        one_row_pk += 1
    if trouble_time_HT_all > 0 or last_month.trouble_time_HT_all_core > 0:
        one_row_pk += 1
    if trouble_time_KR_all > 0 or last_month.trouble_time_KR_all_core > 0:
        one_row_pk += 1
    if trouble_time_CN_all > 0 or last_month.trouble_time_CN_all_core > 0:
        one_row_pk += 1
    if trouble_time_GB_all > 0 or last_month.trouble_time_GB_all_core > 0:
        one_row_pk += 1

    #####################################

    if trouble_time_ALL_login >0 or last_month.trouble_time_ALL_login_core >0:
        ALL_row_pk += 1
        one_row_pk += 1
    if trouble_time_ALL_store > 0 or last_month.trouble_time_ALL_store_core > 0:
        ALL_row_pk += 1
        one_row_pk += 1
    if trouble_time_ALL_register > 0 or last_month.trouble_time_ALL_register_core > 0:
        ALL_row_pk += 1
        one_row_pk += 1
    if trouble_time_ALL_game > 0 or last_month.trouble_time_ALL_game_core > 0:
        ALL_row_pk += 1
        one_row_pk += 1
    if trouble_time_ALL_all > 0 or last_month.trouble_time_ALL_all_core > 0:
        ALL_row_pk += 1
        one_row_pk += 1
    ################################

    if ALL_row >0:
        one_row +=1
    if ALL_row >0 or ALL_row_pk>0:
        one_row_pk +=1

   ################################

    if trouble_time_all == 0:
        trouble_time_all = 1
    else:
        pass


    ##########################二级指标展示判断############################
    rowspan_AE = 0
    rowspan_AE_1 = 0
    list_AE = []


    if trouble_time_AE_active > 0 or last_month.trouble_time_AE_active >0:
        rowspan_AE +=1
        dic_AE = [u'活动',trouble_time_AE_active,last_month.trouble_time_AE_active]
        list_AE.append(dic_AE)
    if trouble_time_AE_active > 0:
        rowspan_AE_1 += 1


    if trouble_time_AE_platform > 0 or last_month.trouble_time_AE_platform >0:
        rowspan_AE += 1
        dic_AE = [u'平台', trouble_time_AE_platform,last_month.trouble_time_AE_platform]
        list_AE.append(dic_AE)
    if trouble_time_AE_platform > 0 :
        rowspan_AE_1 += 1


    if trouble_time_AE_backstage > 0 or last_month.trouble_time_AE_backstage>0:
        rowspan_AE += 1
        dic_AE = [u'后台', trouble_time_AE_backstage,last_month.trouble_time_AE_backstage]
        list_AE.append(dic_AE)
    if trouble_time_AE_backstage > 0:
        rowspan_AE_1 += 1

    if trouble_time_AE_other > 0 or last_month.trouble_time_AE_other>0:
        rowspan_AE += 1
        dic_AE = [u'其他',trouble_time_AE_other,last_month.trouble_time_AE_other]
        list_AE.append(dic_AE)
    if trouble_time_AE_other > 0 :
        rowspan_AE_1 += 1


    ##########################二级指标展示判断############################
    rowspan_HT = 0
    rowspan_HT_1 = 0
    list_HT = []


    if trouble_time_HT_active > 0 or last_month.trouble_time_HT_active>0:
        rowspan_HT +=1
        dic_AE = [u'活动', trouble_time_HT_active,last_month.trouble_time_HT_active]
        list_HT.append(dic_AE)
    if trouble_time_HT_active > 0 :
        rowspan_HT_1 += 1

    if trouble_time_HT_platform > 0 or last_month.trouble_time_HT_platform>0:
        rowspan_HT += 1
        dic_AE = [u'平台', trouble_time_HT_platform,last_month.trouble_time_HT_platform]
        list_HT.append(dic_AE)
    if trouble_time_HT_platform > 0 :
        rowspan_HT_1 += 1

    if trouble_time_HT_backstage > 0 or last_month.trouble_time_HT_backstage>0:
        rowspan_HT += 1
        dic_AE = [u'后台', trouble_time_HT_backstage,last_month.trouble_time_HT_backstage]
        list_HT.append(dic_AE)
    if trouble_time_HT_backstage > 0 :
        rowspan_HT_1 += 1

    if trouble_time_HT_other > 0 or last_month.trouble_time_HT_other>0:
        rowspan_HT += 1
        dic_AE = [u'其他', trouble_time_HT_other,last_month.trouble_time_HT_other]
        list_HT.append(dic_AE)
    if trouble_time_HT_other > 0 :
        rowspan_HT_1 += 1

    ##########################二级指标展示判断############################
    rowspan_KR = 0
    rowspan_KR_1 = 0
    list_KR = []


    if trouble_time_KR_active > 0 or last_month.trouble_time_KR_active>0:
        rowspan_KR +=1
        dic_AE = [u'活动', trouble_time_KR_active,last_month.trouble_time_KR_active]
        list_KR.append(dic_AE)
    if trouble_time_KR_active > 0 :
        rowspan_KR_1 += 1

    if trouble_time_KR_platform > 0 or last_month.trouble_time_KR_platform>0:
        rowspan_KR += 1
        dic_AE = [u'平台', trouble_time_KR_platform,last_month.trouble_time_KR_platform]
        list_KR.append(dic_AE)
    if trouble_time_KR_platform > 0 :
        rowspan_KR_1 += 1

    if trouble_time_KR_backstage > 0 or last_month.trouble_time_KR_backstage>0:
        rowspan_KR += 1
        dic_AE = [u'后台', trouble_time_KR_backstage,last_month.trouble_time_KR_backstage]
        list_KR.append(dic_AE)
    if trouble_time_KR_backstage > 0 :
        rowspan_KR_1 += 1

    if trouble_time_KR_other > 0 or last_month.trouble_time_KR_other>0:
        rowspan_KR += 1
        dic_AE = [u'其他', trouble_time_KR_other,last_month.trouble_time_KR_other]
        list_KR.append(dic_AE)
    if trouble_time_KR_other > 0:
        rowspan_KR_1 += 1


    ##########################二级指标展示判断############################
    rowspan_CN = 0
    rowspan_CN_1 = 0
    list_CN = []


    if trouble_time_CN_active > 0 or last_month.trouble_time_CN_active>0:
        rowspan_CN +=1
        dic_AE = [u'活动', trouble_time_CN_active,last_month.trouble_time_CN_active]
        list_CN.append(dic_AE)
    if trouble_time_CN_active > 0 :
        rowspan_CN_1 += 1

    if trouble_time_CN_platform > 0 or last_month.trouble_time_CN_platform>0:
        rowspan_CN += 1
        dic_AE = [u'平台', trouble_time_CN_platform,last_month.trouble_time_CN_platform]
        list_CN.append(dic_AE)
    if trouble_time_CN_platform > 0 :
        rowspan_CN_1 += 1

    if trouble_time_CN_backstage > 0 or last_month.trouble_time_CN_backstage>0:
        rowspan_CN += 1
        dic_AE = [u'后台', trouble_time_CN_backstage,last_month.trouble_time_CN_backstage]
        list_CN.append(dic_AE)
    if trouble_time_CN_backstage > 0 :
        rowspan_CN_1 += 1

    if trouble_time_CN_other > 0 or last_month.trouble_time_CN_other>0:
        rowspan_CN += 1
        dic_AE = [u'其他', trouble_time_CN_other,last_month.trouble_time_CN_other]
        list_CN.append(dic_AE)
    if trouble_time_CN_other > 0 :
        rowspan_CN_1 += 1


    ##########################二级指标展示判断############################
    rowspan_GB = 0
    rowspan_GB_1 = 0
    list_GB = []


    if trouble_time_GB_active > 0 or last_month.trouble_time_GB_active>0:
        rowspan_GB +=1
        dic_AE = [u'活动', trouble_time_GB_active,last_month.trouble_time_GB_active]
        list_GB.append(dic_AE)
    if trouble_time_GB_active > 0 :
        rowspan_GB_1 += 1

    if trouble_time_GB_platform > 0 or last_month.trouble_time_GB_platform>0:
        rowspan_GB += 1
        dic_AE = [u'平台', trouble_time_GB_platform,last_month.trouble_time_GB_platform]
        list_GB.append(dic_AE)
    if trouble_time_GB_platform > 0 :
        rowspan_GB_1 += 1

    if trouble_time_GB_backstage > 0 or last_month.trouble_time_GB_backstage>0:
        rowspan_GB += 1
        dic_AE = [u'后台', trouble_time_GB_backstage,last_month.trouble_time_GB_backstage]
        list_GB.append(dic_AE)
    if trouble_time_GB_backstage > 0:
        rowspan_GB_1 += 1

    if trouble_time_GB_other > 0 or last_month.trouble_time_GB_other>0:
        rowspan_GB += 1
        dic_AE = [u'其他', trouble_time_GB_other,last_month.trouble_time_GB_other]
        list_GB.append(dic_AE)
    if trouble_time_GB_other > 0:
        rowspan_GB_1 += 1




    export_excel.monthrepo(**locals())

    export_month = request.form.get('month', None)
    file_name = u'%s月故障分析.xlsx' % export_month
    return Response(r'http://%s/static/files/report/%s' % (request.host,file_name))



