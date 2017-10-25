//{# 重构关闭样式。关闭后刷新页面 #}
$('.t_button').click(function(){
    $(this).hide();
    location.href = '/auth/manager_users';
})


//{# 删除用户功能 #}
function del_infomation(id){
    if(window.confirm("确定要删除吗?")) {
        $.get(
            '/auth/user_delete',
            {'id': id},
            function (data) {
                if(data['code'] == 200){
                    location.href = '/auth/manager_users';
                }
            }
        )
    }
}

//{# 修改页面提交按钮 #}
function user_button(id){
    var telphone = $('.m_telphone').val();
    var email = $('.m_email').val();
    var password = $('.m_password').val();
    var department = $('.m_department').val();
    var roles = $('.m_roles').val();
    var permission = $('.m_permission').val();
    var user_status = $('.m_status').val();


    if(telphone == 'None' || telphone == ''){
        alert('手机号码无效，请输入正确！');
        return;
    }else if(email == 'None' || email == ''){
        alert('邮箱地址无效，请输入正确！');
        return;
    }

    $.post(
        '/auth/user_update',
        {
            'id':id,
            'telphone':telphone,
            'email':email,
            'password':password,
            'department':department,
            'roles':roles,
            'permission':permission,
            'user_status':user_status
        },function(data){
            if(data['code'] == 200){
                location.href = '/auth/manager_users';
            }else{
                if(data['message']){
                    alert(data['message']);
                }else{
                    alert('添加异常');
                }
            }
        }
    )

}


//{# 改变password的状态 #}
function edit_password(){
    $('.m_password').attr('disabled',false);
}



//{# 按钮 弹框可修改用户资料 #}
function edit_infomation(id){
    $('#alert_size').show();
    $.get(
        '/auth/edit_user',
        {'id':id},
        function(data){
            $('.alert_size').show()
            $('.t_text').text('修改个人资料')
            $('.t_content').html(data);
        }
    )
}

//{# 监控search中输入的信息，页面上会针对性显示 #}
$('.search').bind('input propertychange',function(){
    var This_value = $(this).val();
    $('.show_user').each(function(){
        var html_message = $(this).text().trim();
        if( html_message.indexOf(This_value) != -1){
            $(this).show()
        }else{
            $(this).hide()
        }
    })
});


//{# 用户创建提交表单post方式 #}
$('#create_user').click(function(event){
    event.preventDefault();

    var username = $('#username').val();
    var department = $('#department').val();
    var permission = $('#permission').val()

    //{# 判断email username telphone是否为空 #}
    if(username == ''){
        alert('用户名称不能为空！')
        return;
    }

    $.post(
        '/auth/manager_users',
        {
            'username':username,
            'department':department,
            'permission':permission
        },function(data){
            if (data['code'] == 400){
                alert(data['message']);
            }
            location.href = '/auth/manager_users';
        }
    )
});