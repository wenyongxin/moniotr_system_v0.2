#!/usr/bin/env python
#ecoding:utf-8


'''
功能：
主要用户验证码的生成
icon图标的展示
业务管理模块
'''


from flask import render_template, request, Response
from flask_login import login_required, current_user
from . import auth
from .. import db
from ..models import Icon, Permission_Model, User
from ..business.models import Manager_business
from ..scripts.xtcaptcha import Captcha
from io import BytesIO
from ..decorators import admin_required


#验证码视图函数
@auth.route('/captcha')
def captcha():
    text, image = Captcha.gene_code()
    #通过StringIO这个类来将图片当成流的形式返回给客户端
    out = BytesIO()  #获取管道
    image.save(out, 'png')  #把图片保存到管道中
    out.seek(0) #移动指针到第0个位置，如果不移动下面无法正常读取到该图片
    response = Response(out.read(),content_type='image/png')
    return response


#图标样式框
@auth.route('/manager_icon', methods=['GET'])
@login_required
@admin_required
def manager_icon():
    icon = Icon.query.all()
    icon_list = [icon[i:i + 50] for i in range(0, len(icon), 50)]
    page = request.args.get('page')
    if page:
        html_all = "<div class=\"close_icons\" onclick=\"close_button()\"><div>&times;</div></div><ul>"
        for icon in icon_list[int(page) - 1]:
            html = '''<li onclick=\"change_icon('%s')\"><span class="glyphicon %s"></span></li>''' %(icon.icon_name,icon.icon_name)
            html_all += html
        html_all += '''</ul>
                        <div class=\"i_page\">
                            <a onclick=\"page_up(%s)\">上一个</a>
                            <span>&nbsp;%s/4&nbsp;</span>
                            <a onclick=\"page_down(%s)\">下一个</a>
                        </div>''' %(page, page, page)
        return html_all


#用于控制显示该管理组具有管理那些管理权限
def return_checks(id, get_dict=None):
    #处理流程
    #1、循环当前所有的版块标题信息。
    #2、将循环的信息跟受到权限制约的信息比较。如果包含则返回true，否则返回false
    #3、在通过输入版块名称从有权限制约的模板中获取二级目录的列表信息
    #4、每个版块下的二级目录信息与第三部操作返回的做对比。如果包含返回true，其它全部返回false
    #5、整理出列表嵌套字典格式数据
    #格式例子：
    #[{'section':[<aaaa>,true], 'urls':[[<bbbbbb>,true], [<ccccc>,false], [<dddd>,true]]}]
    def find_urls(section_name, head=None):
        check_sections = []
        for a in current_user.sesctions(id):
            if head:
                check_sections.append(a['section'])
            else:
                if section_name == a['section']:
                    return a['urls']
                    break
        if head:
            return check_sections

    all_result,result_dict = [],{}
    for i in current_user.sesctions():
        if i['section'] in find_urls(i['section'], True):
            section_results = [i['section'], 'true']
            if get_dict:
                result_dict[int(i['section'].id)] = u'true'
        else:
            section_results = [i['section'], 'false']
            if get_dict:
                result_dict[int(i['section'].id)] = u'false'
        check_urls = []
        for url in i['urls']:
            if find_urls(i['section']):
                if url in find_urls(i['section']):
                    urls_result = [url, 'true']
                    if get_dict:
                        result_dict[int(url.id)] = u'true'
                else:
                    urls_result = [url, 'false']
                    if get_dict:
                        result_dict[int(url.id)] = u'false'
            else:
                urls_result = [url, 'false']
                if get_dict:
                    result_dict[int(url.id)] = u'false'
            check_urls.append(urls_result)
        all_result.append({'section':section_results, 'urls':check_urls})
    if get_dict:
        return result_dict
    else:
        return all_result


#路径访问权限展示树
@auth.route('/tree', methods=['GET'])
@login_required
@admin_required
def tree():
    id = request.args.get('id')
    all_result = return_checks(id)

    #当前权限的信息
    permission = Permission_Model.query.filter_by(id=id).first()
    return render_template('manager/alert_tree.html', all_result=all_result, permission=permission)


#路径访问权限展示树
@auth.route('/change_avatar', methods=['GET'])
@login_required
def change_avatar():
    userid = current_user.id
    http_data = {
        'name':u'修改头像',
        'user':db.session.query(User).filter(User.id == userid).first()
    }
    return  render_template('manager/change_avatar.html', **http_data)


#用于做业务数据的管理
#1、可定义规则，定义该规则名称，并制定该下面包含哪些itemid
#2、通过itemid方式获取当前的值
#3、制定在哪个url路径上显示。
#4、改url路径实现一劳永逸。只需要后面传参就可以自动分辨

@auth.route('/manager_business', methods=['GET','POST'])
@admin_required
@login_required
def manager_business():
    business = db.session.query(Manager_business).order_by(Manager_business.sections_id, Manager_business.sort).all()

    html_data = {
        'name' : u'业务监控管理',
        'business' : business
    }
    return render_template('manager/manager_business.html', **html_data)